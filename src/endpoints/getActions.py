import json
import logging
from flask import jsonify, request
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

def getActionText(app):
    """ This function is used to get the action from the text 
    Args:
        app: The Flask app
    """ 

    systemInstruction = '''Eres Tepoz, un asistente bancario experto de Banorte. Tu objetivo es identificar las acciones que el usuario quiere realizar con base en el texto proporcionado. Las acciones disponibles son: 'realizar_transaccion', 'analisis_financiero', 'preguntas_frecuentes', 'seguridad' y 'request_info_or_ans' que es usado para pedir más información o dar seguimiento.

    - Para 'realizar_transaccion', necesitas obtener dos datos: 'amount' (una cantidad) y 'recipient' (un nombre proporcionado por el usuario).
    - Para 'analisis_financiero', necesitas la 'category' que especifique el área a analizar.
    - Para 'preguntas_frecuentes', necesitas que el usuario te proporcione una 'question'.
    - Si no se cuenta con suficiente información para ejecutar una acción, debes pedir los detalles faltantes al usuario antes de continuar.

    Si el texto recibido no tiene la información necesaria para ejecutar la acción solicitada, solicita los datos faltantes de manera clara y precisa hasta que tengas lo suficiente para proceder. Solo ejecuta una acción cuando toda la información requerida esté disponible.
    '''

    

    @app.route('/get-action-from-text', methods=['POST'])
    def get_action():
        try:
            if request.content_type != 'application/json':
                return jsonify({'error': 'Content-Type must be application/json'}), 415
            
            history_data = request.get_json()

            print(history_data)
            
            INITIAL_PROMPT = f'''
            Si tienes suficiente información, debes generar un esquema de JSON para la acción correspondiente. Si no, debes solicitar los datos faltantes al usuario es decir, debes pedir los detalles faltantes al usuario antes de continuar.
            Para las transacciones es importante que pidas el nombre de la persona o la cuenta a la que se quiere mandar el dinero.

            Historial de conversación:
            {history_data}
            

            - Para 'realizar_transaccion', usa el siguiente formato:
            {{
                "action": "realizar_transaccion",
                "amount": "cantidad",
                "recipient": "nombre"
                "concept": "concepto"
            }}
            - Para 'analisis_financiero', usa el siguiente formato:
            {{
                "action": "analisis_financiero",
                "category": "categoria"
            }}
            - Para 'preguntas_frecuentes', usa el siguiente formato:
            {{
                "action": "preguntas_frecuentes",
                "question": "pregunta"
            }}
            - Para 'seguridad', usa el siguiente formato:
            {{
                "action": "seguridad"
                "input": "input"
            }}
            - Para 'request_info_or_ans', usa el siguiente formato:
            {{
                "action": "request_info_or_ans"
                "ans": "answer"
            }}
            '''
            model = genai.GenerativeModel("gemini-1.5-flash-latest",
                system_instruction = systemInstruction
            )

            response = model.generate_content(
                INITIAL_PROMPT,
                generation_config={"response_mime_type": "application/json"},
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
                }
            )

            response_data = json.loads(response.text)

            if response_data["action"] == "realizar_transaccion":
                print("Realizar transacción")
                pass

            logging.debug(f"Obtained response: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            logging.error(f"Error during fetching content: {str(e)}", exc_info=True)
            return jsonify({'error': f'Error al obtener el contenido: {str(e)}'}), 500