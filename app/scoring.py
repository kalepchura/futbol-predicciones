from datetime import datetime, timezone


def calcular_puntos(
    pred_local: int,
    pred_visitante: int,
    real_local: int,
    real_visitante: int,
    fecha_prediccion: datetime,
    fecha_partido: datetime,
) -> int:
    puntos = 0

    exacto = pred_local == real_local and pred_visitante == real_visitante

    # R1 — Resultado exacto
    if exacto:
        puntos += 5
    else:
        # R2 — Ganador correcto (solo si no fue exacto)
        ganador_pred = (pred_local > pred_visitante) - (pred_local < pred_visitante)
        ganador_real = (real_local > real_visitante) - (real_local < real_visitante)
        if ganador_pred == ganador_real:
            puntos += 3

        # R3 — Diferencia de goles correcta (solo si no fue exacto)
        if (pred_local - pred_visitante) == (real_local - real_visitante):
            puntos += 2

    # R5 — Predicción anticipada (>24h antes del partido)
    if fecha_prediccion.tzinfo is None:
        fecha_prediccion = fecha_prediccion.replace(tzinfo=timezone.utc)
    if fecha_partido.tzinfo is None:
        fecha_partido = fecha_partido.replace(tzinfo=timezone.utc)

    if (fecha_partido - fecha_prediccion).total_seconds() > 86400:
        puntos += 1

    return puntos


def calcular_bonus_racha(predicciones_ordenadas: list) -> int:
    """
    Recibe lista de tuplas (pred_local, pred_visit, real_local, real_visit)
    ordenadas cronológicamente por fecha del partido.
    Retorna bonus acumulado por R4 (cada 3 aciertos consecutivos de ganador = +2).
    """
    racha = 0
    bonus = 0
    for pred_local, pred_visit, real_local, real_visit in predicciones_ordenadas:
        ganador_pred = (pred_local > pred_visit) - (pred_local < pred_visit)
        ganador_real = (real_local > real_visit) - (real_local < real_visit)
        if ganador_pred == ganador_real:
            racha += 1
            if racha % 3 == 0:
                bonus += 2
        else:
            racha = 0
    return bonus