from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ejecutar', methods=['POST'])
def ejecutar_script():
    try:
        # Obtener el texto de entrada del usuario
        data = request.get_json()
        texto_entrada = data.get('texto', '')
        
        # Ejecuta tu fichero Python pasando el texto como argumento
        # Opción 1: Pasar como argumento de línea de comandos
        resultado = subprocess.run(['python3', 'script.py', texto_entrada], 
                                 capture_output=True, 
                                 text=True, 
                                 timeout=3000)
        
        # Opción 2: Si tu script lee de stdin, descomenta estas líneas y comenta las de arriba
        # resultado = subprocess.run(['python3', 'tu_fichero.py'], 
        #                          input=texto_entrada,
        #                          capture_output=True, 
        #                          text=True, 
        #                          timeout=30)
        
        return jsonify({
            'success': True,
            'output': resultado.stdout,
            'error': resultado.stderr,
            'input': texto_entrada
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)