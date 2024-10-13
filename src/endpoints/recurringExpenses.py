import requests
import json
import logging
from flask import jsonify
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def getRecurringExpenses(app):
    """ This function is used to get the action from the text 
    Args:
        app: The Flask app
    """

    systemInstruction = '''
    Eres Maya, un asistente bancario experto de Banorte. Tu objetivo es identificar los pagos que repito cada cierta fecha, me preguntaras si quiero pagarlas este mes de nuevo. Puedes guiarte por las fechas.

    Un ejemplo puede ser que todos los meses pago la renta, y tú me notifiques si quiero pagarla este mes de nuevo. Ten en cuenta los tiempos de compra ya que una sola compra no puede ser relevante a menos de que sea innecesaria y los conceptos.

    Los titulos tienen que tener relación con el nombre del copcepto, ejemplo:  "Ya viene la renta este mes", "Es hora de pagar la mensualidad del GYM", "En una semana tienes que pagar spotify", "¿Sigues usando tu suscripcion de HBO MAX?", y que sean llamativos para captar la atención de la persona pero concisos y que se entienda.

    La descripcion tengo pensado algo asi: "Maya ha notado un pago recurrente de ... entre los dias ... y ... de los meses pasados, ¿quieres hacer el pago este mes?

    No uses palabras como: compulsivo, impulsivo y sus derivados.
    '''

    @app.route('/recurringExpenses', methods=['GET'])
    def get_recurring_expenses():
        try:
            response = requests.get('https://backend-banorte-328383011109.us-central1.run.app/api/movimientos/get/dto/usuario/5')

            if response.status_code != 200:
                return jsonify({'error': 'No se pudo obtener el historial de transacciones'}), 400

            transaction_history = response.json()

            if not transaction_history:
                return jsonify({'error': 'No se proporcionó un historial de transacciones válido'}), 400
            
            # Generar la solicitud inicial para el modelo con un llamado explícito a obtener múltiples recomendaciones
            INITIAL_PROMPT = f'''
            Con los siguientes datos, identificar los pagos que repito cada cierta fecha, me preguntaras si quiero pagarlas este mes de nuevo.
            Sino encuentras un nombre simulalo.

            Transacciones:
            {transaction_history}

            Por cada recomendación, sigue el formato: 
            {{
                "Title": "Título llamativo para captar la atención de la persona",
                "description": "Breve descripción de la recomendación",
                "status": "pagado o no pagado",
                "name": "Nombre del que recibe el pago",
                "monto": "Monto de la transacción",
                "concepto": "Concepto de la transacción",

            }}

            Si tienes varias recomendaciones,solo retorname una en solo JSON.
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