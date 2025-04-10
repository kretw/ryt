from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///club.db"
app.secret_key = "secret_key"
db = SQLAlchemy(app)

@app.route('/offer', methods=['GET'])
def offer():
    phone = "+" + request.args.get('phone', '').replace(" ", "")
    trainer = request.args.get('trainer', '')
    date = request.args.get('date', '')
    time = request.args.get('time', '')
    type_training = request.args.get('type_training', '')
    kind = request.args.get('kind', '')
    comments = request.args.get('comments', '')

    # Создаем запись
    offer = Offer(phone=phone, trainer=trainer, date=date, time=time, 
                  type_training=type_training, kind=kind, text=comments)
    try:
        db.session.add(offer)
        db.session.commit()
        return "Запись успешно сохранена!", 200
    except Exception as e:
        return f"Ошибка при сохранении записи: {str(e)}", 500

# Модель администратора
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Модель записи клиентов
class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)
    trainer = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(10), nullable=False)
    kind = db.Column(db.String(50), nullable=False)
    type_training = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text)

# Модель лошадей
class Horse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

@app.route('/')
@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html')

@app.route('/galery')
def galery():
    return render_template('galery.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/photo')
def photo():
    return render_template('photo.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/recording', methods=['GET', 'POST'])
def recording():
    if request.method == 'POST':
        try:
            # Получение данных из формы
            phone = "+" + request.form['phone'].replace(" ", "")
            trainer = request.form['trainer']
            date = request.form['date']
            time = request.form['time']
            type_training = request.form['type_training']
            kind = request.form['kind']
            text = request.form.get('comments', '')  # По умолчанию пусто, если комментарий отсутствует
            horse_id = request.form.get('horse_id')

            # Создание новой записи
            offer = Offer(phone=phone, trainer=trainer, date=date, time=time, 
                          type_training=type_training, kind=kind, text=text)

            # Добавление записи в базу данных
            db.session.add(offer)
            db.session.commit()

            # Обновляем статус лошади, если лошадь выбрана
            if horse_id:
                selected_horse = Horse.query.get(horse_id)
                if selected_horse and selected_horse.is_available:
                    selected_horse.is_available = False
                    db.session.commit()

            return redirect(url_for('about'))  # Перенаправление на главную страницу после успешной записи
        except Exception as e:
            return f"Произошла ошибка записи: {str(e)}"  # Отображение ошибки

    # Отображение страницы с доступными лошадьми
    horses = Horse.query.filter_by(is_available=True).all()
    return render_template('recording.html', horses=horses)

# Панель входа администратора
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            return redirect(url_for('admin_panel'))
        else:
            return "Неверное имя пользователя или пароль", 401
    return render_template('admin_login.html')

# Панель администратора
@app.route('/admin/panel')
def admin_panel():
    offers = Offer.query.all()
    horses = Horse.query.all()
    trainers = get_trainers()
    return render_template('admin_panel.html', offers=offers, horses=horses, trainers=trainers)

# Удаление записи клиента
@app.route('/admin/offers/delete/<int:offer_id>', methods=['POST'])
def delete_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    return redirect(url_for('admin_panel'))

# Фильтрация записей по тренеру
@app.route('/admin/filter', methods=['POST'])
def filter_offers():
    trainer = request.form.get('trainer')
    filtered_offers = Offer.query.filter_by(trainer=trainer).all()
    return render_template('admin_panel.html', offers=filtered_offers, trainers=get_trainers())

# Вспомогательная функция для получения списка тренеров
def get_trainers():
    return [offer.trainer for offer in Offer.query.distinct(Offer.trainer).all()]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(username="admin", password="admin")
            db.session.add(admin)
            db.session.commit()
    app.run(port=int(os.environ.get("PORT", 3001)))

# Отображение списка лошадей в админской панели
@app.route('/admin/horses', methods=['GET'])
def admin_horses():
    horses = Horse.query.all()
    return render_template('admin_horses.html', horses=horses)

# Добавление новой лошади
@app.route('/admin/horses/add', methods=['POST'])
def add_horse():
    name = request.form['name']
    horse = Horse(name=name, is_available=True)
    db.session.add(horse)
    db.session.commit()
    return redirect(url_for('admin_horses'))


# Редактирование лошади
@app.route('/admin/horses/edit/<int:horse_id>', methods=['GET', 'POST'])
def edit_horse(horse_id):
    horse = Horse.query.get_or_404(horse_id)
    if request.method == 'POST':
        horse.name = request.form['name']
        horse.is_available = 'is_available' in request.form
        db.session.commit()
        return redirect(url_for('admin_horses'))
    return render_template('edit_horse.html', horse=horse)

# Удаление лошади
@app.route('/admin/horses/delete/<int:horse_id>', methods=['POST'])
def delete_horse(horse_id):
    horse = Horse.query.get_or_404(horse_id)
    db.session.delete(horse)
    db.session.commit()
    return redirect(url_for('admin_horses'))

# Редактирование записи клиента
@app.route('/admin/offers/edit/<int:offer_id>', methods=['GET', 'POST'])
def edit_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if request.method == 'POST':
        offer.phone = request.form['phone']
        offer.trainer = request.form['trainer']
        offer.date = request.form['date']
        offer.time = request.form['time']
        offer.kind = request.form['kind']
        offer.type_training = request.form['type_training']
        offer.text = request.form['comments']
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('edit_offer.html', offer=offer)

# Экспорт данных в Excel
@app.route('/admin/export', methods=['GET'])
def export_to_excel():
    try:
        offers = Offer.query.all()
        if not offers:
            return "Нет данных для экспорта.", 400
        data = [{
            "Phone": offer.phone,
            "Trainer": offer.trainer,
            "Date": offer.date,
            "Time": offer.time,
            "Kind": offer.kind,
            "Type of Training": offer.type_training,
            "Comments": offer.text
        } for offer in offers]
        df = pd.DataFrame(data)
        file_path = os.path.join(os.getcwd(), "client_offers.xlsx")
        df.to_excel(file_path, index=False)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Произошла ошибка: {str(e)}", 500
