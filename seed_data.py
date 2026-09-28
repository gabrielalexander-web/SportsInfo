"""
Inserta deportes de ejemplo con todos los campos nuevos (equipamiento,
beneficios físicos, puntajes de comparación) en Supabase.
Ejecuta: python seed_data.py
"""
from supabase_client import supabase

DEPORTES_EJEMPLO = [
    {
        "name": "Fútbol", "category": "Equipo", "gender": "Mixto",
        "description": "Deporte de equipo jugado con los pies, muy popular en Bolivia y Latinoamérica.",
        "how_it_works": "Dos equipos de 11 jugadores intentan meter el balón en el arco contrario usando cualquier parte del cuerpo menos las manos (excepto el arquero).",
        "average_cost": "Bajo (~$30-60 en botines y balón)", "cost_score": 2,
        "time_commitment": "3-6 horas/semana", "time_score": 3, "funding_score": 5,
        "difficulty_level": "Principiante",
        "equipment_required": "Botines, espinilleras, balón, ropa deportiva.",
        "physical_benefits": "Mejora resistencia cardiovascular, velocidad, coordinación y fuerza en piernas.",
        "recommendations": "Empieza con partidos informales o una liga barrial. Trabaja resistencia cardiovascular y técnica de pase.",
        "diet_recommendations": "Carbohidratos complejos antes del partido, buena hidratación y proteína magra para recuperación.",
        "image_url": "",
    },
    {
        "name": "Natación", "category": "Acuático", "gender": "Mixto",
        "description": "Ejercicio de bajo impacto que trabaja todo el cuerpo, ideal para resistencia y fuerza.",
        "how_it_works": "Se nada en piscina o aguas abiertas usando distintos estilos (libre, espalda, pecho, mariposa), compitiendo por tiempo en distancias definidas.",
        "average_cost": "Medio (membresía de piscina + traje de baño)", "cost_score": 3,
        "time_commitment": "3-4 horas/semana", "time_score": 3, "funding_score": 3,
        "difficulty_level": "Intermedio",
        "equipment_required": "Traje de baño, gorro, gafas de natación, acceso a piscina.",
        "physical_benefits": "Trabaja todo el cuerpo, mejora capacidad pulmonar y es de bajo impacto para las articulaciones.",
        "recommendations": "Toma clases de técnica antes de nadar largas distancias. Progresa gradualmente en distancia.",
        "diet_recommendations": "Proteína para recuperación muscular, carbohidratos para energía prolongada, hidratación constante.",
        "image_url": "",
    },
    {
        "name": "Running", "category": "Individual", "gender": "Mixto",
        "description": "Correr al aire libre o en cinta, uno de los deportes más accesibles.",
        "how_it_works": "Consiste en correr distancias variables a distintos ritmos, desde trote suave hasta carreras de velocidad o larga distancia.",
        "average_cost": "Bajo (par de buenas zapatillas ~$60-100)", "cost_score": 1,
        "time_commitment": "2-5 horas/semana", "time_score": 2, "funding_score": 2,
        "difficulty_level": "Principiante",
        "equipment_required": "Zapatillas adecuadas, ropa deportiva transpirable.",
        "physical_benefits": "Mejora resistencia cardiovascular, quema calórica alta, fortalece piernas.",
        "recommendations": "Empieza con caminata-trote, invierte en buen calzado y aumenta distancia progresivamente (regla del 10%).",
        "diet_recommendations": "Carbohidratos antes de correr distancias largas, electrolitos en climas cálidos, proteína después.",
        "image_url": "",
    },
    {
        "name": "Ciclismo", "category": "Individual", "gender": "Mixto",
        "description": "Deporte de resistencia sobre bicicleta, en ruta o montaña.",
        "how_it_works": "Se recorre distancia sobre bicicleta, en carretera o montaña, individualmente o en grupo, midiendo tiempo o distancia.",
        "average_cost": "Alto (bicicleta + equipo de seguridad)", "cost_score": 5,
        "time_commitment": "3-8 horas/semana", "time_score": 4, "funding_score": 3,
        "difficulty_level": "Intermedio",
        "equipment_required": "Bicicleta, casco, luces, ropa técnica, kit de reparación.",
        "physical_benefits": "Fortalece piernas, mejora resistencia cardiovascular, bajo impacto articular.",
        "recommendations": "Usa siempre casco, aprende mantenimiento básico de la bici y planifica rutas seguras.",
        "diet_recommendations": "Carbohidratos de absorción lenta antes de salidas largas, geles o frutas durante el recorrido.",
        "image_url": "",
    },
    {
        "name": "Boxeo", "category": "Combate", "gender": "Mixto",
        "description": "Deporte de combate que mejora fuerza, reflejos y condición cardiovascular.",
        "how_it_works": "Dos boxeadores se enfrentan usando solo golpes de puño, dentro de categorías de peso, siguiendo reglas estrictas de seguridad.",
        "average_cost": "Medio (guantes, vendas, clases en gimnasio)", "cost_score": 3,
        "time_commitment": "3-5 horas/semana", "time_score": 3, "funding_score": 4,
        "difficulty_level": "Intermedio",
        "equipment_required": "Guantes, vendas, protector bucal, saco de boxeo (en el gimnasio).",
        "physical_benefits": "Mejora fuerza, reflejos, coordinación y condición cardiovascular; alivia estrés.",
        "recommendations": "Aprende técnica básica con un entrenador antes de practicar sparring. Cuida la protección de manos y cabeza.",
        "diet_recommendations": "Proteína suficiente para desarrollo muscular, control de peso según categoría, buena hidratación.",
        "image_url": "",
    },
    {
        "name": "Yoga", "category": "Individual", "gender": "Mixto",
        "description": "Práctica que combina posturas físicas, respiración y meditación.",
        "how_it_works": "Se practican secuencias de posturas (asanas) combinadas con respiración controlada, buscando flexibilidad, fuerza y calma mental.",
        "average_cost": "Bajo (mat de yoga + clases opcionales)", "cost_score": 1,
        "time_commitment": "2-4 horas/semana", "time_score": 2, "funding_score": 1,
        "difficulty_level": "Principiante",
        "equipment_required": "Mat de yoga, ropa cómoda.",
        "physical_benefits": "Mejora flexibilidad, equilibrio y postura; reduce estrés y tensión muscular.",
        "recommendations": "Empieza con clases guiadas (presenciales o en video) para aprender posturas correctamente.",
        "diet_recommendations": "Alimentación ligera antes de practicar, buena hidratación, dieta equilibrada rica en vegetales.",
        "image_url": "",
    },
    {
        "name": "Básquetbol", "category": "Equipo", "gender": "Mixto",
        "description": "Velocidad, saltos y precisión bajo el aro — puro ritmo de equipo en cada posesión.",
        "how_it_works": "Dos equipos de 5 jugadores buscan encestar el balón en el aro contrario, driblando y pasando dentro de una cancha rectangular.",
        "average_cost": "Bajo (~$25-50 en zapatillas y balón)", "cost_score": 2,
        "time_commitment": "3-5 horas/semana", "time_score": 3, "funding_score": 4,
        "difficulty_level": "Principiante",
        "equipment_required": "Zapatillas con buen agarre, balón, ropa deportiva.",
        "physical_benefits": "Mejora salto, coordinación, velocidad y trabajo en equipo.",
        "recommendations": "Practica el dribleo básico antes de sumarte a partidos completos.",
        "diet_recommendations": "Carbohidratos antes del partido, hidratación constante por el ritmo intenso.",
        "image_url": "",
    },
    {
        "name": "Vóley", "category": "Equipo", "gender": "Mixto",
        "description": "Reflejos, saltos y comunicación — cada punto se gana en equipo, en el aire.",
        "how_it_works": "Dos equipos de 6 jugadores se turnan para golpear el balón por encima de una red, sin dejarlo caer en su propio campo.",
        "average_cost": "Bajo (~$20-40 en rodilleras y balón)", "cost_score": 1,
        "time_commitment": "3-4 horas/semana", "time_score": 2, "funding_score": 3,
        "difficulty_level": "Principiante",
        "equipment_required": "Rodilleras, ropa deportiva, balón, acceso a cancha con red.",
        "physical_benefits": "Mejora salto, reflejos, coordinación y trabajo en equipo.",
        "recommendations": "Aprende primero el toque y la recepción antes de sumarte a un partido.",
        "diet_recommendations": "Comidas ligeras antes de jugar, buena hidratación.",
        "image_url": "",
    },
    {
        "name": "Tenis", "category": "Individual", "gender": "Mixto",
        "description": "Estrategia, precisión y resistencia mental, punto a punto, en la cancha.",
        "how_it_works": "Dos jugadores (o parejas) se enfrentan golpeando la pelota con una raqueta por encima de la red, buscando que el rival no pueda devolverla.",
        "average_cost": "Medio-alto (raqueta + clases + cancha)", "cost_score": 4,
        "time_commitment": "3-5 horas/semana", "time_score": 3, "funding_score": 3,
        "difficulty_level": "Intermedio",
        "equipment_required": "Raqueta, pelotas, zapatillas específicas, acceso a cancha.",
        "physical_benefits": "Mejora reflejos, resistencia, coordinación y fuerza en el tren superior.",
        "recommendations": "Toma clases para aprender el golpe correcto desde el inicio; evita lesiones de codo.",
        "diet_recommendations": "Hidratación constante, carbohidratos antes de partidos largos.",
        "image_url": "",
    },
    {
        "name": "Artes Marciales", "category": "Combate", "gender": "Mixto",
        "description": "Disciplina, control y confianza — un deporte que se entrena tanto en el cuerpo como en la mente.",
        "how_it_works": "Incluye disciplinas como taekwondo, karate o judo: técnica de golpes, derribos o llaves, practicadas con un compañero bajo reglas y supervisión de un instructor.",
        "average_cost": "Medio (uniforme + mensualidad de dojo)", "cost_score": 3,
        "time_commitment": "2-4 horas/semana", "time_score": 2, "funding_score": 3,
        "difficulty_level": "Principiante",
        "equipment_required": "Uniforme (gi/dobok), protector bucal, acceso a un dojo o gimnasio.",
        "physical_benefits": "Mejora flexibilidad, disciplina, fuerza y coordinación; alivia estrés.",
        "recommendations": "Empieza en un dojo con instructor certificado; progresa por cinturones a tu ritmo.",
        "diet_recommendations": "Alimentación balanceada, buena hidratación antes de las clases.",
        "image_url": "",
    },
]


def main():
    if supabase is None:
        print("❌ No hay conexión a Supabase. Configura tu archivo .env primero.")
        return
    for deporte in DEPORTES_EJEMPLO:
        try:
            supabase.table("sports").insert(deporte).execute()
            print(f"✅ Insertado: {deporte['name']}")
        except Exception as exc:
            print(f"⚠️  Error insertando {deporte['name']}: {exc}")


if __name__ == "__main__":
    main()
