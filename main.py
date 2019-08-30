from flask import Flask, escape, request, jsonify, Response
import pyodbc
from json import dumps
import functools
from datetime import datetime
import random
import hashlib
import math
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

now = datetime.now()
app = Flask(__name__,template_folder='view',static_folder='dist')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

env_pruebas = "https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu/"
env_produccion = "https://checkout.payulatam.com/ppp-web-gateway-payu/"
apikey = "uzIc90bkpXj0aJDh22H67MRJnl"
merchantId = 530932
accountId = 532826
PORCENTAJE_IVA = 19

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=190.85.232.78;DATABASE=DBKiero_Productos;UID=sa;PWD=S3rv3r1-27!')

# def get_products(category):
#     cursor = collection.find({"Categoria_id":str(category),"Titulo": { "$exists": True }},{"_id":False}).sort([("Titulo", 1)]).limit(5)
#     return (cursor)
def generar_referencia_payu(idProduct,idUser):
    # fecha_trans = datetime.now().strftime('%Y%m%d')
    # reference_code = '{0}.{1}-KIERO'.format(fecha_trans,str(id))
    # return reference_code
    date_time = now.strftime("%m%d%Y%H%M")
    numberCodeRandom = (random.randint(100000,900000))
    reference_code = "KIERO_{idProduct}_{idUser}_{date}_{numberCodeRandom}".format(idProduct=idProduct,idUser=idUser,date=date_time,numberCodeRandom=numberCodeRandom)
    return reference_code

def generar_firma(apiKey,merchantId,referenceCode,amount,currency):
    algoritmo = hashlib.md5()
    hash = '{0}~{1}~{2}~{3}~{4}'.format(apiKey,merchantId,referenceCode,amount,currency)
    algoritmo.update(hash.encode('utf-8'))
    return algoritmo.hexdigest()

@app.route('/<int:idUser>/<int:idProduct>/<int:quantity>', methods=('GET', 'POST'))
def pagos(idUser,idProduct,quantity):
    if request.method == 'GET':
        with conn:
            query = """select * from users where id = {idUser} or idGoogle = {idUser}""".format(idUser=idUser)
            crsr = conn.execute(query)
            user = crsr.fetchone()
        if not user:
            flash({"code":0,"message":"el usuario no existe"})
            return render_template('index.html', url = env_pruebas)
        
        with conn:
            query = """select * from tbl_Productos where Producto_Id = {}""".format(idProduct)
            crsr = conn.execute(query)
            product = crsr.fetchone()

        with conn:
            query = """SELECT * FROM addresses_users_kiero where id_user = {}""".format(idUser)
            crsr = conn.execute(query)
            address = crsr.fetchone()

        if not product:
            flash({"code":0,"message":"El producto no existe o esta inhabilitado"})
            return render_template('index.html', url = env_pruebas)
        referencecode = (generar_referencia_payu(idProduct,idUser))

        aumento = math.ceil((int(product.Precio_cop) * quantity) * (PORCENTAJE_IVA / 100)) # Dividir entre 100 porque es un porcentaje
        amount = (int(product.Precio_cop) * quantity) - aumento
        total = int(product.Precio_cop) * quantity

        firma = generar_firma(apikey,merchantId,referencecode,total,'COP')
        
        return render_template('index.html', url = env_produccion,user=user,product=product,merchantId=merchantId,accountId=accountId,referencecode=referencecode,firma=firma, aumento=aumento,amount=amount,address=address)

if __name__ == "__main__":
    app.run(host='10.4.28.90',debug=True)



