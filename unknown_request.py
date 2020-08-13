from flask import Flask, Response, request, make_response, jsonify




app = Flask(__name__)


@app.route('/', methods=['POST'])
def main():

        print(request.args)
        print(request.json)
        print(request.form)

    asd="asd"66
    szam = 213
    return
    return jsonify({'ewrt': asd, 'wert': szam})
    return jsonify(asd = asd, szam = szam)

if __name__ == '__main__':
        app.run()