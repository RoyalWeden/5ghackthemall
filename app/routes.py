from app import app, config
from flask import redirect, render_template, session, url_for, request
from app.database import SQLConnection

sqlconn = SQLConnection()
sqlconn.execute_sql(sqlconn.drop_tables)

@app.route('/')
def home():
    create_session_user()
    return render_template('home.html', session=session)

@app.route('/admin', methods=['GET','POST'])
def admin():
    create_session_user()
    if 'email' in session:
        if 'verify' in request.args:
            return redirect('/admin')

        return render_template('admin.html')
    elif 'verify' in request.args:
        if request.args['verify'] != config['VERIFY_ADMIN_ID']:
            return redirect('/')

        if request.method == 'POST':
            if request.form['signtype'] == 'signup':
                email = sqlconn.execute_sql(sqlconn.set_admin_user, session['user_id'], request.form['email'], request.form['password'])
                print("Signed Up:", email)
            elif request.form['signtype'] == 'signin':
                user_id = sqlconn.execute_sql(sqlconn.is_admin_user, request.form['email'], request.form['password'])
                if user_id != None:
                    session['user_id'] = user_id
                    session['email'] = request.form['email']
                    print("Signed In:", session['email'])
                    return redirect('/admin')

        return render_template('admin.html')
    else:
        return redirect('/')

@app.route('/admin/signout')
def signout():
    create_session_user()
    if 'email' in session:
        session.pop('email', None)
    return redirect('/admin')

@app.route('/admin/edit-profile', methods=['GET','POST'])
def edit_profile():
    create_session_user()
    if 'email' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = sqlconn.execute_sql(
            sqlconn.edit_profile,
            session['user_id'],
            request.form['profile_firstname'],
            request.form['profile_lastname'],
            request.form['personal_link1'],
            request.form['personal_link2']
        )
        print("Profile Updated", name)
        return redirect('/admin/edit-profile')

    user_profile = sqlconn.execute_sql(sqlconn.get_profile, session['user_id'])

    return render_template('edit_profile.html', user_profile=user_profile)

def create_session_user():
    if 'user_id' not in session:
        session['user_id'] = sqlconn.execute_sql(sqlconn.create_user)
    else:
        if sqlconn.execute_sql(sqlconn.get_user, session['user_id']) == None:
            sqlconn.execute_sql(sqlconn.create_user, session['user_id'])
    print('User ID:', session['user_id'])


@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')