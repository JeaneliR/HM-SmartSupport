from services.classifier_service import fallback_classification, parse_classification


def test_parse_normalizes_allowed_values():
    result = parse_classification(
        {
            "categoria": "falla",
            "prioridad": "critica",
            "equipo": "remalladora",
            "problema": "humo",
            "requiere_atencion_tecnica": True,
            "recomendacion": "Detener el uso.",
        }
    )
    assert result.categoria == "Falla"
    assert result.prioridad == "Crítica"
    assert result.requiere_atencion_tecnica is True


def test_critical_fallback_for_smoke():
    result = fallback_classification("Mi remalladora bota humo y huele a quemado")
    assert result.categoria == "Falla"
    assert result.prioridad == "Crítica"
    assert result.requiere_atencion_tecnica is True


def test_out_of_domain_fallback():
    result = fallback_classification("¿Quién ganará el partido?")
    assert result.categoria == "Otros"
    assert result.prioridad == "Baja"


def test_string_false_is_not_truthy():
    result = parse_classification(
        {
            "categoria": "Información",
            "prioridad": "Baja",
            "equipo": "máquina de coser",
            "problema": "consulta general",
            "requiere_atencion_tecnica": "false",
            "recomendacion": "Orientar al cliente.",
        }
    )
    assert result.requiere_atencion_tecnica is False
