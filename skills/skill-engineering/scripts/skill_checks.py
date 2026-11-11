"""Validação estrutural de skills; não mede qualidade de modelos.

Python 3.10+. PyYAML é necessário somente para validate_skill.
"""
import argparse
import json
import math
import re
import statistics
from pathlib import Path
from urllib.parse import unquote

PORTABLE_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


class InputError(ValueError):
    """Entrada ou execução inválida, apresentável sem traceback na CLI."""


def markdown_links(text):
    """Extraia destinos inline/imagem e definições, ignorando código Markdown."""
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            mark = marker[1]
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            continue
        if fence is None and not line.startswith(("    ", "\t")):
            lines.append(line)
    text = re.sub(r"(`+).*?\1", "", "\n".join(lines), flags=re.S)
    starts = r"!?\[[^\]\n]*\]\(\s*|^ {0,3}\[[^\]\n]+\]:\s*"
    for match in re.finditer(starts, text, flags=re.M):
        tail = text[match.end():]
        if tail.startswith("<"):
            end = tail.find(">")
            if end >= 0:
                yield tail[1:end]
            continue
        chars, depth, index = [], 0, 0
        while index < len(tail):
            char = tail[index]
            if char == "\\" and index + 1 < len(tail) and tail[index + 1] in "()\\":
                chars.append(tail[index + 1])
                index += 2
                continue
            if (char.isspace() or char == ")") and depth == 0:
                break
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            chars.append(char)
            index += 1
        if chars:
            yield "".join(chars)


def _read_markdown(path, root, errors):
    if not path.resolve().is_relative_to(root):
        errors.append(f"Arquivo escapa da raiz: {path}")
        return None
    if not path.is_file():
        errors.append(f"Arquivo ausente: {path.relative_to(root)}")
        return None
    return path.read_text(encoding="utf-8")


def _audit_links(text, source, root, errors):
    for target in markdown_links(text):
        if not target or target.startswith("#"):
            continue
        decoded = unquote(target).replace("\\", "/")
        absolute = decoded.startswith("/") or re.match(r"^[A-Za-z]:", decoded)
        scheme = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*):", decoded)
        if scheme and scheme[1].lower() != "file" and not absolute:
            continue
        if absolute or scheme:
            errors.append(f"{source.name}: link absoluto proibido: {target}")
            continue
        relative = decoded.split("#", 1)[0].split("?", 1)[0]
        if not relative:
            continue
        path = source.parent / relative
        if not path.resolve().is_relative_to(root):
            errors.append(f"{source.name}: link escapa da raiz: {target}")
        elif not path.exists():
            errors.append(f"{source.name}: link ausente: {target}")


def validate_skill(directory, profile="hermes"):
    """Retorne valid/errors/warnings; erros do alvo são distintos de InputError."""
    if profile not in {"portable", "hermes"}:
        raise InputError("Perfil deve ser hermes ou portable")
    root = Path(directory).resolve()
    if not root.is_dir():
        raise InputError(f"Diretório inexistente ou inválido: {directory}")
    try:
        import yaml
    except ImportError as exc:
        raise InputError("Validação exige PyYAML instalado") from exc
    errors, warnings = [], []
    text = _read_markdown(root / "SKILL.md", root, errors)
    if text is not None:
        parts = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", text, re.S)
        if not parts:
            errors.append("SKILL.md exige frontmatter delimitado por ---")
        else:
            try:
                header = yaml.safe_load(parts[1])
            except yaml.YAMLError as exc:
                header = None
                errors.append(f"YAML inválido: {exc}")
            if not isinstance(header, dict) or not header:
                errors.append("Frontmatter deve ser um mapping não vazio")
            else:
                name = header.get("name")
                if not isinstance(name, str) or len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                    errors.append("name exige 1 a 64 caracteres minúsculos, dígitos e hífens simples internos")
                elif name != root.name:
                    errors.append("name deve coincidir com o diretório")
                description = header.get("description")
                limit = 60 if profile == "hermes" else 1024
                if not isinstance(description, str) or not description.strip() or len(description) > limit:
                    errors.append(f"description deve ser texto não vazio com até {limit} caracteres")
                if profile == "portable":
                    extra = set(header) - PORTABLE_FIELDS
                    if extra:
                        errors.append(f"Campos fora do perfil portable: {', '.join(sorted(map(str, extra)))}")
            if not parts[2].strip():
                errors.append("Corpo de SKILL.md não pode ser vazio")
            _audit_links(parts[2], root / "SKILL.md", root, errors)
        if len(text.splitlines()) > 500:
            warnings.append("Mais de 500 linhas: convenção de tamanho, não medida de qualidade")
    refs = root / "references"
    if refs.exists() and not refs.resolve().is_relative_to(root):
        errors.append("references escapa da raiz")
    elif refs.is_dir():
        for path in sorted(refs.glob("*.md")):
            content = _read_markdown(path, root, errors)
            if content is not None:
                _audit_links(content, path, root, errors)
    return {"valid": not errors, "profile": profile, "directory": str(root),
            "errors": errors, "warnings": warnings,
            "scope": "Structure only; does not certify quality, discovery or model performance."}


CONDITIONS = ("with_skill", "baseline")
STATUSES = ("completed", "technical_error", "not_run")
METRICS = ("duration_ms", "input_tokens", "output_tokens", "cost_usd")
REQUIRED = {"case_id", "replicate", "condition", "status", "task_success", "critical_failures"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"Chave JSON duplicada: {key}")
        result[key] = value
    return result


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise InputError(f"Número JSON não finito: {text}")
    return value


def load_results(filename):
    """Leia JSON estrito, rejeitando chaves repetidas e NaN/Infinity."""
    return json.loads(Path(filename).read_text(encoding="utf-8"),
                      object_pairs_hook=_unique_object, parse_float=_finite_float,
                      parse_constant=_finite_float)


def _validate_run(run, index):
    prefix = f"runs[{index}]"
    if not isinstance(run, dict) or not REQUIRED.issubset(run):
        raise InputError(f"{prefix}: registro ou campos obrigatórios inválidos")
    if not isinstance(run["case_id"], str) or not run["case_id"].strip():
        raise InputError(f"{prefix}: case_id deve ser texto não vazio")
    if type(run["replicate"]) is not int or run["replicate"] <= 0:
        raise InputError(f"{prefix}: replicate deve ser inteiro positivo")
    if run["condition"] not in CONDITIONS or run["status"] not in STATUSES:
        raise InputError(f"{prefix}: condition ou status inválido")
    success, failures = run["task_success"], run["critical_failures"]
    if run["status"] == "completed":
        if type(success) is not bool or type(failures) is not int or failures < 0:
            raise InputError(f"{prefix}: completed exige bool task_success e inteiro critical_failures >= 0")
    elif success is not None or failures is not None:
        raise InputError(f"{prefix}: execução não concluída exige indicadores null")
    for metric in METRICS:
        value = run.get(metric)
        if value is None:
            continue
        integer = metric.endswith("tokens")
        valid_type = type(value) is int if integer else type(value) in (int, float)
        if not valid_type or value < 0 or (type(value) is float and not math.isfinite(value)):
            raise InputError(f"{prefix}: {metric} exige número finito não negativo, tokens inteiros")


def _summary(values):
    return {"mean": statistics.mean(values) if values else None,
            "sample_stddev": statistics.stdev(values) if len(values) > 1 else None}


def aggregate_runs(data):
    """Agregue somente pares completed do schema de references/avaliacao.md.

    baseline: without_skill|old_skill; condition: with_skill|baseline.
    schema_version, quando informado, deve ser o inteiro 1. Ausências de
    métricas permanecem desconhecidas. Delta positivo é nova menos baseline.
    """
    if not isinstance(data, dict) or data.get("baseline") not in ("without_skill", "old_skill"):
        raise InputError("baseline deve ser without_skill ou old_skill")
    version = data.get("schema_version", 1)
    if type(version) is not int or version != 1 or not isinstance(data.get("runs"), list):
        raise InputError("schema_version deve ser 1 e runs deve ser um array")
    groups, inconsistencies = {}, []
    counts = {condition: dict(total=0, completed=0, technical_error=0, not_run=0)
              for condition in CONDITIONS}
    for index, run in enumerate(data["runs"]):
        _validate_run(run, index)
        condition = run["condition"]
        group = groups.setdefault((run["case_id"], run["replicate"]), {})
        if condition in group:
            raise InputError(f"Chave caso/repetição/condição duplicada em runs[{index}]")
        group[condition] = run
        counts[condition]["total"] += 1
        counts[condition][run["status"]] += 1
        if run["status"] == "completed" and run["task_success"] and run["critical_failures"] > 0:
            inconsistencies.append({key: run[key] for key in ("case_id", "replicate", "condition")})
    complete = [group for group in groups.values()
                if len(group) == 2 and all(run["status"] == "completed" for run in group.values())]
    n = len(complete)
    missing = sum(len(group) < 2 for group in groups.values())
    success = {"n_pairs": n}
    for condition in CONDITIONS:
        successes = sum(group[condition]["task_success"] and group[condition]["critical_failures"] == 0
                        for group in complete)
        success[condition] = {"successes": successes, "rate_pct": 100 * successes / n if n else None}
    success["delta_pp"] = (success["with_skill"]["rate_pct"] - success["baseline"]["rate_pct"]) if n else None
    metrics = {}
    for metric in METRICS:
        observed = [group for group in complete
                    if all(group[condition].get(metric) is not None for condition in CONDITIONS)]
        summary = {"n_pairs": len(observed)}
        for condition in CONDITIONS:
            summary[condition] = _summary([group[condition][metric] for group in observed])
        summary["delta_mean"] = (summary["with_skill"]["mean"] - summary["baseline"]["mean"]) if observed else None
        metrics[metric] = summary
    return {"baseline": data["baseline"], "run_count": len(data["runs"]), "conditions": counts,
            "pairs": {"total": len(groups), "completed": n, "incomplete": len(groups) - n,
                      "missing_condition": missing, "non_completed": len(groups) - n - missing},
            "success": success, "metrics": metrics, "inconsistencies": inconsistencies,
            "inconsistency_count": len(inconsistencies),
            "scope": "Aggregation trusts supplied records; no independent quality or discovery assessment."}


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


def main(argv=None):
    """Execute a CLI: 0 válido, 1 pacote inválido, 2 erro de entrada/execução."""
    parser = _Parser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Validar estrutura do pacote")
    validate.add_argument("directory")
    validate.add_argument("--profile", choices=("hermes", "portable"), default="hermes")
    aggregate = commands.add_parser("aggregate", help="Agregar resultados pareados")
    aggregate.add_argument("file")
    try:
        args = parser.parse_args(argv)
        if args.command == "validate":
            report = validate_skill(args.directory, args.profile)
            status = 0 if report["valid"] else 1
        else:
            report = aggregate_runs(load_results(args.file))
            status = 0
        output = json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2)
    except (OSError, ValueError, RuntimeError, OverflowError) as exc:
        status = 2
        output = json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False)
    print(output)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
