import json
import logging
from flask import jsonify
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def getRecomendationsSpends(app):
    """ This function is used to get the action from the text 
    Args:
        app: The Flask app
    """ 

    systemInstruction = '''
    Eres Tepoz, un asistente bancario experto de Banorte. Tu objetivo es identificar los gastos que pueden estar afectando mis finanzas. Puedes guiarte por los conceptos o montos, es importante que los gastos esenciales como comida y renta no se consideren, ya que son necesarios.
    Un ejemplo puede ser que se esté gastando en dos servicios de streaming; uno de ellos podría eliminarse para ahorrar dinero. Otro ejemplo sería identificar compras impulsivas. Ten en cuenta los tiempos de compra ya que una sola compra no puede ser relavante a menos de que sea innecesaria y los conceptos. Para la relevancia hay dos, 'prioritario' o 'no_prioritario'.

    Los titulos tienen que tener relación con el nombre del copcepto, ejemplo:  "Tus gastos en Starbucks están por las nubes", "Cuidado con el café: Tu cuenta de Starbucks está creciendo", "¡No lo dejes pasar! Estás gastando más en ropa que en ahorros", "¡Basta! Tu amor por el streaming está drenando tus finanzas", "!A la moda pero con medida! Tus gastos en ropa merecen atención" y que sean llamativos para captar la atención de la persona pero concisos y que se entienda.

    No uses palabras como: compulsivo, impulsivo y sus derivados.
    '''

    @app.route('/SpendingShield', methods=['GET'])
    def get_recomendations_spends():
        try:
            # Historial de transacciones simulado
            transaction_history = [
                {
                    "descripcion": "Supermercado",
                    "tipo": "Compra",
                    "monto": 150.0,
                    "fecha": "2024-10-01T14:35:20.911+00:00"
                },
                {
                    "descripcion": "Restaurante",
                    "tipo": "Ocio",
                    "monto": 85.5,
                    "fecha": "2024-10-02T19:45:10.911+00:00"
                },
                {
                    "descripcion": "Netflix",
                    "tipo": "Suscripción",
                    "monto": 12.99,
                    "fecha": "2024-10-03T08:30:45.911+00:00"
                },
                {
                    "descripcion": "HBO max",
                    "tipo": "Transferencia",
                    "monto": 100.0,
                    "fecha": "2024-10-12T23:13:36.911+00:00"
                },
                {
                    "descripcion": "Ropa",
                    "tipo": "Ocio",
                    "monto": 60.0,
                    "fecha": "2024-10-05T22:00:00.911+00:00"
                },
                {
                    "descripcion": "Pago de alquiler",
                    "tipo": "Gasto fijo",
                    "monto": 500.0,
                    "fecha": "2024-10-05T10:15:30.911+00:00"
                },
                {
                    "descripcion": "Ropa",
                    "tipo": "Compra",
                    "monto": 200.0,
                    "fecha": "2024-10-07T16:20:50.911+00:00"
                },
                {
                    "descripcion": "Starbucks",
                    "tipo": "Ocio",
                    "monto": 20.0,
                    "fecha": "2024-10-09T17:40:00.911+00:00"
                },
                {
                    "descripcion": "Gimnasio",
                    "tipo": "Gasto fijo",
                    "monto": 35.0,
                    "fecha": "2024-10-10T09:00:00.911+00:00"
                },
                {
                    "descripcion": "Cine",
                    "tipo": "Ocio",
                    "monto": 25.0,
                    "fecha": "2024-10-11T21:10:00.911+00:00"
                }
            ]

            if not transaction_history:
                return jsonify({'error': 'No se proporcionó un historial de transacciones válido'}), 400
            
            # Generar la solicitud inicial para el modelo con un llamado explícito a obtener múltiples recomendaciones
            INITIAL_PROMPT = f'''
            Con los siguientes datos, analiza mis gastos para identificar aquellos que sean innecesarios o puedan ser optimizados para mejorar mis finanzas. Considera que puedes encontrar más de una recomendación.

            Transacciones:
            {transaction_history}

            Por cada recomendación, sigue el formato:
            {{
                "Title": "Título llamativo para captar la atención de la persona",
                "description": "Breve descripción de la recomendación",
                "relevance": "Importancia"
            }}

            Si tienes varias recomendaciones, proporciónalas todas en un solo JSON.
            '''

            # Inicializar el modelo generativo
            model = genai.GenerativeModel("gemini-1.5-flash-latest", system_instruction=systemInstruction)

            # Generar el contenido
            response = model.generate_content(
                INITIAL_PROMPT,
                generation_config={"response_mime_type": "application/json"},
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
                }
            )

            response_data = json.loads(response.text)

            # Comprobar si el modelo generó recomendaciones
            if not response_data:
                return jsonify({'message': 'No se encontraron gastos innecesarios.'}), 200

            logging.debug(f"Response data: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            logging.error(f"Error during content generation: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error al generar el contenido: {str(e)}'}), 500

