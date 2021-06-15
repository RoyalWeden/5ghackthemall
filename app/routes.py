from app import app, config
from flask import redirect, render_template, session, url_for, request
from app.database import SQLConnection

sqlconn = SQLConnection()
sqlconn.execute_sql(sqlconn.drop_tables)

@app.route('/')
def home():
    create_session_user()
    documents = sqlconn.execute_sql(sqlconn.get_all_documents)
    return render_template(
        'home.html',
        session=session,
        documents=documents
    )

@app.route('/5g-overview')
def overview5g():
    create_session_user()
    documents = sqlconn.execute_sql(sqlconn.get_all_documents)
    for i in range(len(documents)-1, -1, -1):
        if documents[i]['document_type'] != '5G Overview':
            documents.pop(i)
    return render_template(
        'overview5g.html',
        session=session,
        documents=documents
    )

@app.route('/use-cases')
def use_cases():
    create_session_user()
    documents = sqlconn.execute_sql(sqlconn.get_all_documents)
    for i in range(len(documents)-1, -1, -1):
        if documents[i]['document_type'] != 'Use Case':
            documents.pop(i)
    return render_template(
        'use_cases.html',
        session=session,
        documents=documents
    )

@app.route('/admin', methods=['GET','POST'])
def admin():
    create_session_user()
    if 'email' in session:
        if 'verify' in request.args:
            return redirect('/admin')

        if request.method == 'POST':
            if request.form['type'] == 'add_document':
                document_id = sqlconn.execute_sql(
                    sqlconn.create_document,
                    session['user_id'],
                    request.form['document_type'],
                    request.form['document_title'],
                    request.form['document_summary'],
                    request.form['document_description'],
                    request.form['document_relevantlink1'],
                    request.form['document_relevantlink2'],
                    request.form['document_relevantlink3'],
                    request.form['document_relevantlink4'],
                    request.form['document_relevantlink5']
                )
                print("New Document", document_id, sqlconn.execute_sql(sqlconn.get_document, document_id))

        return render_template('admin.html')
    elif 'verify' in request.args:
        if request.args['verify'] != config['VERIFY_ADMIN_ID']:
            return redirect('/')

        if request.method == 'POST':
            if request.form['type'] == 'signup':
                email = sqlconn.execute_sql(sqlconn.set_admin_user, session['user_id'], request.form['email'], request.form['password'])
                print("Signed Up:", email)
            elif request.form['type'] == 'signin':
                user_id = sqlconn.execute_sql(sqlconn.is_admin_user, request.form['email'], request.form['password'])
                if user_id != None:
                    session['user_id'] = user_id
                    session['email'] = request.form['email']
                    print("Signed In:", session['email'])
                    return redirect('/admin')
                return redirect('/')

        return render_template('admin.html')
    else:
        return redirect('/')

@app.route('/admin/signout')
def signout():
    create_session_user()
    if 'email' in session:
        session.pop('email', None)
    return redirect('/admin/?verify=' + config['VERIFY_ADMIN_ID'])

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

@app.route('/document/<document_id>')
def view_document(document_id):
    create_session_user()
    document = sqlconn.execute_sql(sqlconn.get_document, document_id)
    return render_template('document.html', document=document)

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