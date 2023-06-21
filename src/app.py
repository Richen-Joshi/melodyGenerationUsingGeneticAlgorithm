from flask import Flask, render_template, request
from mgen import main, generate
from pathlib import Path

app = Flask(__name__)

app.global_pop = []


@app.route('/result', methods=("GET", "POST"))
def result():
    if request.method == "POST":
        check = int(request.form['check'])
        if check == 0:
            nbar = int(request.form['nbar'])
            notes = int(request.form['notes'])
            nsteps = int(request.form['nsteps'])
            pause = request.form['pause']
            if pause == "True":
                pause = True
            else:
                pause=False
            key = request.form['key']
            scale = request.form['scale']
            scaleroot = int(request.form['scaleroot'])
            population = int(request.form['population'])
            nmutations = int(request.form['nmutations'])
            probability = int(request.form['probability'])
            beats = int(request.form['beats'])
            app.global_pop = main(nbar, notes, nsteps, pause, key, scale,
                                  scaleroot, population, nmutations, probability, beats)
            return render_template('result.html', result=population, mut=nmutations, prob=probability, nbar=nbar, notes=notes, nsteps=nsteps, pause=pause, key=key, scale=scale, scaleroot=scaleroot, beats=beats)
        else:
            print(app.global_pop)
            # Rating
            ratings = []
            population = int(request.form['population'])
            nmutations = int(request.form['mut'])
            probability = int(request.form['prob'])
            nbar = int(request.form['nbar'])
            notes = int(request.form['notes'])
            nsteps = int(request.form['nsteps'])
            pause = request.form['pause']
            if pause == "True":
                pause = True
            key = request.form['key']
            scale = request.form['scale']
            scaleroot = int(request.form['scaleroot'])
            beats = int(request.form['beats'])

            print(population)
            for i in range(population):
                ratings.append(int(request.form[str(i)]))
            app.global_pop = generate(ratings, nmutations, probability, app.global_pop,nbar,notes,nsteps,pause,key,scale,scaleroot,beats)
            return render_template('result.html', result=population, mut=nmutations, prob=probability, nbar=nbar, notes=notes, nsteps=nsteps, pause=pause, key=key, scale=scale, scaleroot=scaleroot, beats=beats)


@app.route('/', methods=("GET", "POST"))
def index():

    return render_template('add_task.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
