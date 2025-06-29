from flask import Flask, request, send_file, abort
import os
import io
import matplotlib.pyplot as plt
from functions import plot_spectral

app = Flask(__name__)


@app.route('/espectro')
def espectro():
    caminho = request.args.get('arquivo')
    if not caminho or not os.path.exists(caminho):
        return abort(404, description='Arquivo não encontrado')
    try:
        # Gera o gráfico e salva em buffer
        buf = io.BytesIO()
        plot_spectral(caminho, show=False)
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        return f'Erro ao gerar espectro: {e}', 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
