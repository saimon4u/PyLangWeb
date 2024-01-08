from flask import Flask, render_template, request, jsonify

import os
import subprocess
app = Flask(__name__)

@app.route('/', methods=['GET','POST']) 
def process(): 
    if request.method == 'POST':
        filename = 'try.pyL'
        data = request.get_json()['code']
        with open(filename, 'w') as f:
            f.write(data)
            f.close()
        output = subprocess.check_output("python3 Compiler.py try.pyL", shell=True)
        with open('ok.txt', 'wb') as f:
            f.write(output)
            f.close()
        with open('ok.txt', 'r') as f:
            val = f.read() 
            f.close()
        os.remove('ok.txt')
        os.remove('try.pyL')
        return jsonify(data= val)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)