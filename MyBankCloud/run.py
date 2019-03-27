import decimal
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import random as R
import datetime

app = Flask(__name__)

#设置连库字符串
app.config['SQLALCHEMY_DATABASE_URI']="mysql+pymysql://root:123456@localhost:3306/MyBank"
#设置数据库的信号追踪
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#设置执行完视图函数后自动提交操作回数据库
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SECRET_KEY'] = 'aa写'
#设置程序的启动模式为调试模式
#app.config['DEBUG']=True

#创建db
db = SQLAlchemy(app)
# print(db)

#创建Manager对象并指定管理哪个应用(app)
manager = Manager(app)

#创建Migrate对象，并指定关联的app和db
migrate = Migrate(app, db)
#为manager增加命令，允许做数据库的迁移操作
#为manager绑定一个叫db(叫啥可以改)的自定义名字的子命令，该子命令执行操作由MigrateCommand来提供
manager.add_command('db', MigrateCommand)



#考虑要不要创建一个类，用来实现对个人消费记录或转账记录的记载，要由另一个表存储信息，
#信息包括方式(支付，转账，收取)，还有时间与数量，以及所使用的银行卡卡号
class Transfer(db.Model):
    __tablename__ = "transfer"
    id = db.Column(db.Integer, primary_key=True)
    transferidcard = db.Column(
        db.BigInteger,
    )
    operation = db.Column(
        db.String(200),
        nullable=False
    )
    transfertime = db.Column(
        db.String(80),
        default="2019-03-13 20:04:36",
    )

class Teltransfer(db.Model):
    __tablename__ = 'teltransfer'
    id = db.Column(db.Integer, primary_key=True)
    transferidcard = db.Column(
        db.BigInteger,
    )
    teloperation = db.Column(
        db.String(200),
        nullable=False
    )
    teltransfertime = db.Column(
        db.String(80),
        default="2019-03-25 17:23:36",
    )

#创建实体类 - Users,映射到数据库中叫 users 表,此表用来储存客户基本信息
class Users(db.Model):
    __tablename__ = "users"
    #创建字段id,主键,自增
    id = db.Column(db.Integer, primary_key=True)
    #创建字段username,长度为80的字符串，不允许为空,值唯一,加索引
    username = db.Column(
        db.String(80),
        #默认就是不为空
        index=True,
        unique = True,
    )
    #创建字段sex,性别，字符串，不允许为空
    usersex = db.Column(db.String(8))
    #创建字段idcard,身份证号，长度为18的大整数，必须唯一，不允许为空
    idcard = db.Column(
        db.BigInteger,
        unique=True
    )
    #创建字段userpwd，用户密码，字符串，不允许为空，可以修改
    userpwd = db.Column(
        db.String(80)
    )
    #创建字段userphone,用户联系电话，长度为11位的大整数，必须唯一，不允许为空
    userphone = db.Column(
        db.BigInteger,
        unique=True
    )
    #增加字段 isActive,表示用户是否被激活，布尔类型，默认为True
    isActive = db.Column(db.Boolean, default=True)
    #反向引用bankcard表
    bankcard = db.relationship(
        'Bankcard',
        backref='userbkcard',
        lazy='dynamic',
    )

    def __repr__(self):
        return "<User:%r>" % self.username


#创建实体类 - Teller,映射到数据库中叫teller表，此表用来储存柜员基本信息
class Teller(db.Model):
    __tablename__ = 'teller'
    #创建字段id, 主键，自增,同上
    id = db.Column(db.Integer, primary_key=True)
    # 创建字段tellername,长度为80的字符串，不允许为空,加索引
    tellername = db.Column(
        db.String(80),
        index=True
    )
    #创建字段tellcard,柜员身份证号，类型同用户
    tellcard = db.Column(
        db.BigInteger,
        unique=True
    )
    #创建字段tellpwd.柜员登录密码，登录操作以身份证号为帐号，密码自设定，可以修改．
    tellpwd = db.Column(
        db.String(80)
    )

#创建实体类 Bankcard, 映射到数据库中叫bankcard表，用来储存银行卡信息
#银行卡的卡号设置暂定为16位随机数字,或者字符串拼接，如"6231"+"随机生成的12位数字",
#或者"6231" + " " + "随机生成的4位数字" + " " + "随机生成的4位数字" + " " + "随机生成的4位数字"
#注意银行卡号不能出现重复的问题,还有一个人可以拥有多张银行卡
class Bankcard(db.Model):
    __tablename__ = "bankcard"
    #创建字段id, 主键，自增,同上
    id = db.Column(db.Integer, primary_key=True)
    #创建字段bankname，银行名字，标示是那个银行的卡，不允许为空
    bankname = db.Column(
        db.String(80)
    )
    #创建字段banktype
    banktype = db.Column(
        db.String(80)
    )
    #创建字段banknum，卡号，不允许为空，,唯一,长度为16位的大整型，
    banknum = db.Column(
        db.BigInteger,
        unique=True,
        index=True
    )
    #开户名
    username = db.Column(
        db.String(20)
    )
    #创建字段balance，卡上余额,默认为0.00，不能为负
    balance = db.Column(
        db.DECIMAL(10,2),
        default=0.00
    )
    #创建字段cardpwd,支付密码，6位数字,允许为空，用户绑定银行卡是可以设置此密码
    #用于在支付，转账时的密码
    cardpwd = db.Column(
        db.Integer,
        nullable=True
    )
    #银行卡状态onActive，是否激活,布尔类型，默认为True　
    onActive=db.Column(db.Boolean, default=True)
    #增加一个列，引用自Users表的主键列
    user = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
    )



#首页，实现用户登录
@app.route('/', methods=["GET", "POST"])
def hello():
    if request.method == "GET":
        render_template('first.html')
    else:
    #1.获取用户输入的信息（账号及密码）
        cardnum = request.form['username']
        upwd = request.form['upwd']
    #2.获取数据库的帐号及密码信息
        card = Users.query.filter_by(idcard=cardnum).first()
        if card:
            if upwd == card.userpwd:
                session['id'] = card.id
                session['loginname'] = cardnum
                return render_template("second.html", params=locals())
            else:
                msg = "密码错误"
                return render_template("first.html", msg=msg)
        else:
            msg = "账号错误"
            return render_template("first.html", msg=msg)
    #3.对比两个信息
    #4.如果一样，登录成功，进入主界面，不一样则显示帐号或密码错误，返回首页
    return render_template('first.html')

#判断用户登录状态
@app.route('/')
def main_index():
    # 查询Users中的所有分类信息
    allusers = Users.query.all()
    # 判断session中是否由id和loginname
    if 'id' in session and 'loginname' in session:
        # 已经登录,从数据库中获取登录信息
        id = session['id']
        card = Users.query.filter_by(id=id).first()
        return render_template('second.html', params=locals())
    else:
        return render_template('index.html')

# 用户登录判断
def userlogin_judge():
    if 'id' in session and 'loginname' in session:
        # 已经登录,从数据库中获取登录信息
        id = session['id']
        card = Users.query.filter_by(id=id).first()
        return card

# 柜员登录判断
def tellerlogin_judge():
    if 'tid' in session and 'tellername' in session:
         # 已经登录,从数据库中获取登录信息
        tid = session['tid']
        teller = Teller.query.filter_by(id=tid).first()
        return teller


#设置一个路由，目的是实现在网页上的注册功能，并保存到数据库
@app.route('/userregister', methods=["GET", "POST"])
def register_views():
    #判断是GET请求还是POST请求
    if request.method == "GET":
        users = Users.query.all()
        return render_template("user_register.html", users=users)
    else:
        #声明一个变量status用来表示提交数据的状态
        status = 1
        #１．接收请求提交的数据
        username = request.form['username']
        usersex = request.form['usersex']
        idcard = request.form['idcard']
        userphone = request.form['userphone']
        userpwd = request.form['userpwd']
        #２．封装Users的对象
        user = Users()
        user.username = username
        user.usersex = usersex
        user.idcard = idcard
        user.userphone = userphone
        user.userpwd = userpwd
        #３．保存回数据库
        try:
            db.session.add(user)
            # ４．响应
        except Exception as ex:
            print(ex)
            status = 0
        finally:
            if status == 1:
                msg = "恭喜用户注册成功"
                return render_template("user_register.html", msg=msg)
                # return redirect('/user-register')
            else:
                msg = "注册失败，请联系管理员"
                return render_template("user_register.html", msg=msg)


#目的：实现柜员登录界面
@app.route('/teller', methods=["GET", "POST"])
def teller_views():
    if request.method == "GET":
        return render_template('teller.html')
    else:
        tellername = request.form['tellername']
        tpwd = request.form['tpwd']
        teller = Teller.query.filter_by(tellcard=tellername).first()
        if teller:
            if tpwd == teller.tellpwd:
                session['tid'] = teller.id
                session['tellername'] = tellername
                return render_template("teller_index.html", params=locals())
            else:
                msg = "密码有误!"
                return render_template("teller.html", msg=msg)
        else:
            msg = "帐号有误!"
            return render_template("teller.html", msg=msg)

#目的：实现柜员注册界面
@app.route("/teller-register", methods=["GET", "POST"])
def teller_register():
    if request.method == "GET":
        return render_template("teller_register.html")
    else:
        # 声明一个变量status用来表示提交数据的状态
        status = 1
        tellname = request.form['tellname']
        idcard = request.form['idcard']
        tellpwd = request.form['tellpwd']
        tellercard = Teller()
        tellercard.tellername = tellname
        tellercard.tellcard = idcard
        tellercard.tellpwd = tellpwd
        # ３．保存回数据库
        try:
            db.session.add(tellercard)
            # ４．响应
        except Exception as ex:
            print(ex)
            status = 0
        finally:
            if status == 1:
                msg = "柜员注册成功!"
                return render_template("teller_register.html", msg=msg)
            else:
                msg = "柜员注册失败,请联系管理员"
                return render_template("teller_register.html", msg=msg)

#实现查看个人信息的功能
@app.route('/personal', methods=['GET', 'POST'])
def personal_views():
    if request.method == 'GET':
        # 权限验证，判断是否有用户登录，如果没有权限的话
        # 则从哪来回哪去
        # 判断session中是否由idcard和userpwd
        card = userlogin_judge()
        if card:
            #查询bankcard.user为card.id
            bankcards = Bankcard.query.filter_by(
                user=card.id
            ).all()
                # for bank in bankcards:
                #     print(bank)
            return render_template('personal.html', params=locals())
        url = request.headers.get('Referer', '/')
        return redirect(url)


#实现初始操作界面，或在操作页面退出帐号
@app.route('/index')
def index_views():
    return render_template('index.html')

#实现开户功能(办理一张银行卡)
@app.route('/bankcard', methods=['GET', 'POST'])
def bankcard_views():
    L = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    passwd_list = []
    for _ in range(12):
        achar = R.choice(L)
        passwd_list.append(achar)
    bankcardnum = '6231' + ''.join(passwd_list)
    if request.method == "GET":
        card = userlogin_judge()
        if card:
            return render_template('bankcard.html', params=locals())
        url = request.headers.get('Referer', '/')
        return redirect(url)
    else:
        # 声明一个变量status用来表示提交数据的状态
        status = 1
        card = userlogin_judge()
        bankname = request.form['bankname']
        cardtype = request.form['cardtype']
        username = card.username
        cardnum = bankcardnum
        bankcardpwd = request.form['bankcardpwd']
        bkcard = Bankcard()
        bkcard.bankname = bankname
        bkcard.banktype = cardtype
        bkcard.username = username
        bkcard.banknum = cardnum
        bkcard.cardpwd = bankcardpwd
        bkcard.balance = 0.00
        bkcard.user = card.id
        # ３．保存回数据库
        try:
            db.session.add(bkcard)
        except Exception as ex:
            print(ex)
            print('出错了！')
            status = 0
        finally:
            if status == 1:
                msg = "银行卡%s申请成功!"%cardnum
                return render_template('bankcard.html', params=locals())
            else:
                msg = "申请失败,请联系管理员"
                return render_template('bankcard.html', params=locals())

#实现存款功能
@app.route('/savemoney', methods=['GET', 'POST'])
def savemoney_views():
    if request.method == "GET":
        card = userlogin_judge()
        if card:
            # 得到当前登录用户全部的银行卡信息，显示在前端界面
            bankcards = Bankcard.query.filter_by(
                user=card.id
            ).all()
            return render_template('savemoney.html', params=locals())
        url = request.headers.get('Referer', '/')
        return redirect(url)
    else:
        status = 1
        bankcard_id = request.form['banknum']
        print(bankcard_id)
        savemoneys = request.form['moneys']
        pwd = request.form['password']
        bankcard = Bankcard.query.filter_by(
            id=bankcard_id
        ).first()
        card = userlogin_judge()
        bankcards = Bankcard.query.filter_by(
            user=card.id
        ).all()
        if bankcard.onActive == True:
            if int(pwd) == int(bankcard.cardpwd):
                moneys = decimal.Decimal(savemoneys)
                bankcard.balance += moneys
                name1 = card.username
                now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                bkcard = bankcard.banknum
                operation = "%s(您) 向银行卡号为 %d 中存款 %.2f 元" % (name1, int(bkcard), moneys)
                transfer = Transfer()
                #获取用户的身份证号，以身份证号作为区分不同人操作的依据
                transfer.transferidcard = card.idcard
                transfer.operation = operation
                transfer.transfertime = now_time
                try:
                    db.session.commit()
                    db.session.add(transfer)
                except Exception as ex:
                    print(ex)
                    status = 0
                finally:
                    if status == 1:
                        msg = "存款成功!"
                        return render_template('savemoney.html', params=locals())
                    else:
                        msg = "存款失败,请联系管理员"
                        return render_template('savemoney.html', params=locals())
            else:
                msg = "支付密码错误"
                return render_template('savemoney.html', params=locals())
        else:
            msg = '该银行卡已被冻结!无法进行存款业务'
            return render_template('savemoney.html', params=locals())

#实现取款的功能,类似于上
@app.route('/getmoney', methods=['GET', 'POST'])
def getmoney_views():
    if request.method == "GET":
        card = userlogin_judge()
        if card:
            # 得到当前登录用户全部的银行卡信息，显示在前端界面
            bankcards = Bankcard.query.filter_by(
                user=card.id
            ).all()
            return render_template('getmoney.html', params=locals())
        url = request.headers.get('Referer', '/')
        return redirect(url)
    else:
        status = 1
        bankcard_id = request.form['banknum']
        savemoneys = request.form['moneys']
        pwd = request.form['password']
        bankcard = Bankcard.query.filter_by(
            id=bankcard_id
        ).first()
        card = userlogin_judge()
        bankcards = Bankcard.query.filter_by(
            user=card.id
        ).all()
        if bankcard.onActive == True:
            if int(pwd) == int(bankcard.cardpwd):
                getmoneys = decimal.Decimal(savemoneys)
                if bankcard.balance >= getmoneys:
                    bankcard.balance -= getmoneys
                    name1 = card.username
                    now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    bkcard = bankcard.banknum
                    operation = "%s(您) 在银行卡号为 %d 中取款 %.2f 元" % (name1, int(bkcard), getmoneys)
                    transfer = Transfer()
                    transfer.transferidcard = card.idcard
                    transfer.operation = operation
                    transfer.transfertime = now_time
                else:
                    msg = "抱歉，本卡存款不足！"
                    return render_template('getmoney.html', params=locals())
                try:
                    db.session.commit()
                    db.session.add(transfer)
                except Exception as ex:
                    print(ex)
                    print('出错了！')
                    status = 0
                finally:
                    if status == 1:
                        msg = "取款成功!"
                        return render_template('getmoney.html', params=locals())
                    else:
                        msg = "取款失败,请联系管理员"
                        return render_template('getmoney.html', params=locals())
            else:
                msg = "支付密码错误"
                return render_template('getmoney.html', params=locals())
        else:
            msg = '该银行卡已被冻结!无法进行取款业务'
            return render_template('getmoney.html', params=locals())

#实现转账功能
@app.route('/transfer', methods=["GET", "POST"])
def movemoney_views():
    if request.method == "GET":
        card = userlogin_judge()
        if card:
            # 得到当前登录用户全部的银行卡信息，显示在前端界面
            bankcards = Bankcard.query.filter_by(
                user=card.id
            ).all()
            return render_template('transfer.html', params=locals())
        url = request.headers.get('Referer', '/')
        return redirect(url)
    else:
        status = 1
        bankcard_id = request.form['banknum']#转账的..
        getcard = request.form['getcard']#到账的银行卡号
        movemoney = request.form['moneys'] #转账金额
        pwd = request.form['password']
        bankcard = Bankcard.query.filter_by(
            id=bankcard_id
        ).first()
        getmoneycard = Bankcard.query.filter_by(
            banknum=int(getcard)
        ).first()
        card = userlogin_judge()
        bankcards = Bankcard.query.filter_by(
            user=card.id
        ).all()
        if bankcard.onActive == True:
            if getmoneycard.onActive == True:
                if getmoneycard:
                    if int(pwd) == int(bankcard.cardpwd):
                        getmoneys = decimal.Decimal(movemoney)
                        if bankcard.balance >= getmoneys:
                            bankcard.balance -= getmoneys
                            getmoneycard.balance += getmoneys
                            # 将操作转为字符串存入transfer表中
                            # 如"王语嫣 在 2019年3月1日20时06分 把银行卡号为 6231927572307564 中的 <red>100.00<red>
                            # 元转账给用户名为 战神 的银行卡号 6231258530826551 中"
                            # datetime转字符串：
                            # >> > time1_str = datetime.datetime.strftime(time1, '%Y-%m-%d %H:%M:%S')
                            # >> > time1_str
                            # '2014-01-08 11:59:58'
                            #收款方也要有记录：收款人姓名 的银行卡号为 卡号 在 时间 收到来自 转账者姓名 的 钱数 元
                            #通过前端传过来的银行卡号的user属性找到对应的用户id,再用这个在users表中找到对应的用户信息
                            userinfo = Users.query.filter_by(id=getmoneycard.user).first()
                            name2 = userinfo.username   #收款人姓名
                            name2idcard = userinfo.idcard  #收款人的身份证号
                            name1 = card.username #转账者姓名
                            now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            bkcard = bankcard.banknum

                            operation = "%s(您) 把银行卡号为 %d 中的 %.2f 元转账给 用户: %s" % \
                                        (name1, int(bkcard), getmoneys, name2)
                            transfer = Transfer()
                            idcard = session['id']
                            card = Users.query.filter_by(id=idcard).first()
                            transfer.transferidcard = card.idcard
                            transfer.operation = operation
                            transfer.transfertime = now_time

                            operation2 = "%s(您) 的银行卡号为 %d 收到来自 %s 的 %.2f 元" % (name2, int(getcard), name1, getmoneys )
                            transfer2 = Transfer()
                            transfer2.transferidcard = name2idcard
                            transfer2.operation = operation2
                            transfer2.transfertime = now_time
                        else:
                            msg = "抱歉，本卡存款不足！"
                            return render_template('transfer.html', params=locals())
                        try:
                            db.session.commit()
                            db.session.add(transfer)
                            db.session.add(transfer2)
                        except Exception as ex:
                            print(ex)
                            print('出错了！')
                            status = 0
                        finally:
                            if status == 1:
                                msg = "转账成功!"
                                return render_template('transfer.html', params=locals())
                            else:
                                msg = "转账失败,请联系管理员"

                                return render_template('transfer.html', params=locals())
                    else:
                        msg = "支付密码错误"
                        return render_template('transfer.html', params=locals())
                else:
                    msg = "抱歉！该银行卡号不存在！"
                    return render_template('transfer.html', params=locals())
            else:
                msg = '您要转账的银行卡已被冻结!无法进行转账业务'
                return render_template('transfer.html', params=locals())
        else:
            msg = '您的该银行卡已被冻结!无法进行转账业务'
            return render_template('transfer.html', params=locals())

#实现账单功能，记录账户金额操作记录
#1.创建账单数据库(存储用户操作，
# 如"王语嫣 在 2019年3月1日20时06分 把银行卡号为 6231927572307564 中的 <red>100.00<red>
# 元转账给用户名为 战神 的银行卡号 6231258530826551 中"
# 与用户数据库形成关联数据库
@app.route('/moneyforms', methods=["GET", "POST"])
def bill_views():
    if request.method == "GET":
        card = userlogin_judge()
        if card:
            # 得到当前登录用户全部的操作信息，显示在前端界面
            operations = Transfer.query.filter_by(transferidcard=card.idcard).all()
            operations = list(reversed(operations))
            return render_template('bill.html', params=locals())
        url = request.headers.get('Referer', '/')
        return redirect(url)
    else:
        msg = "抱歉！请稍后再试"
        return render_template('bill.html', msg=msg)

#客服中心
@app.route('/release')
def release_views():
    card = userlogin_judge()
    return render_template('release.html', params=locals())

#关于MyBank
@app.route('/about')
def about_views():
    card = userlogin_judge()
    usernum = len(Users.query.all())
    cardnum = len(Bankcard.query.all())
    moneynum = len(Transfer.query.all())
    now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    tellerserver = len(Teltransfer.query.all())
    return render_template('about.html', params=locals())

#实现柜员查询用户信息的功能
@app.route('/tellerIndex', methods=['GET', 'POST'])
def tellerindex_views():
    if request.method == 'GET':
        teller = tellerlogin_judge()
        if teller:
            baseinfo = teller
            return render_template('teller_select.html', params=locals())
        url = request.headers.get('Referer', '/teller')
        return redirect(url)
    else:
        status = 1
        #得到前端输入并传递过来的用户身份证号
        userid = request.form['userid']
        #得到此用户在数据库users表中id号
        baseinfo = Users.query.filter_by(idcard=userid).first()
        if baseinfo:
            uid = baseinfo.id
            #查询此用户信息,包含他／她的银行卡信息
            userinfos = Bankcard.query.filter_by(
                user=baseinfo.id
            ).all()
            msg = '查询成功!'
            teller = tellerlogin_judge()
            now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            operation = "柜员 '%s' 为客户 '%s(%s)' 做查询服务" % (teller.tellername, baseinfo.username, baseinfo.idcard)
            teltransfer = Teltransfer()
            teltransfer.transferidcard = teller.tellcard
            teltransfer.teloperation = operation
            teltransfer.teltransfertime = now_time
            try:
                db.session.commit()
                db.session.add(teltransfer)
            except Exception as ex:
                print(ex)
                status = 0
            finally:
                if status == 1:
                    msg = "查询成功!"
                    return render_template('teller_select.html', params=locals())
                else:
                    msg = "查询失败!"
                    return render_template('teller_select.html', params=locals())
        else:
            teller = []
            msg = '抱歉!该用户不存在'
            return render_template('teller_select.html', params=locals())

#处理激活/冻结账户的功能函数
@app.route('/froggen', methods=['GET', 'POST'])
def froggen_views():
    if request.method == 'GET':
        teller = tellerlogin_judge()
        if teller:
            return render_template('teller_froggen.html', params=locals())
        url = request.headers.get('Referer', '/teller')
        return redirect(url)
    else:
        #从该页面得到信息:柜员选择的具体功能(如:激活银行卡或者冻结银行卡)
        telchoice = request.form['telchoice']
        if telchoice:
            bankcard = request.form['bankcard']
            if bankcard:
                # 得到前端输入的卡号的相关信息
                cardinfos = Bankcard.query.filter_by(banknum=bankcard).first()
                teller = tellerlogin_judge()
                now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                #从数据库获得被修改用户的信息
                userinfo = Users.query.filter_by(id=cardinfos.user).first()
                teltransfer = Teltransfer()
                if telchoice == '激活银行卡':
                    status = 1
                    cardinfos.onActive = True
                    operation = "柜员 '%s' 激活了客户 '%s(%s)' 的银行卡:%s" % (teller.tellername, userinfo.username, userinfo.idcard, bankcard)
                elif telchoice == '冻结银行卡':
                    status = 2
                    cardinfos.onActive = False
                    operation = "柜员 '%s' 冻结了客户 '%s(%s)' 的银行卡:%s" % (
                    teller.tellername, userinfo.username, userinfo.idcard, bankcard)
                else:
                    status = 0
                    msg = '出错!请联系管理员'
                    return render_template('teller_froggen.html', params=locals())
                teltransfer.transferidcard = teller.tellcard
                teltransfer.teloperation = operation
                teltransfer.teltransfertime = now_time
                try:
                    db.session.commit()
                    db.session.add(teltransfer)
                except Exception as ex:
                    print(ex)
                    status = 0
                finally:
                    if status == 1:
                        msg = "激活成功!"
                        return render_template('teller_froggen.html', params=locals())
                    elif status == 2:
                        msg = '冻结成功!'
                        return render_template('teller_froggen.html', params=locals())
                    else:
                        msg = "修改账户状态失败!"
                        return render_template('teller_froggen.html', params=locals())
            else:
                msg = '请输入要修改银行卡号!'
                return render_template('teller_froggen.html', params=locals())
        else:
            msg = '未选择!'
            return render_template('teller_froggen.html', params=locals())

#处理对柜员操作记录的查看
@app.route('/telleractive')
def telleractive_views():
    if request.method == "GET":
        teller = tellerlogin_judge()
        if teller:
            # 得到当前登录用户全部的操作信息，显示在前端界面
            operations = Teltransfer.query.filter_by(transferidcard=teller.tellcard).all()
            operations = list(reversed(operations))
            return render_template('telleractive.html', params=locals())
        url = request.headers.get('Referer', '/teller')
        return redirect(url)
    else:
        msg = "抱歉！请稍后再试"
        return render_template('telleractive.html', msg=msg)

#柜员页面的关于MyBank
@app.route('/telabout')
def telabout_views():
    teller = tellerlogin_judge()
    usernum = len(Users.query.all())
    cardnum = len(Bankcard.query.all())
    moneynum = len(Transfer.query.all())
    now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    tellerserver = len(Teltransfer.query.all())
    return render_template('telabout.html', params=locals())

if __name__=="__main__":
    #manager.run()
    app.run(host = '0.0.0.0' ,port = 5000, debug = 'True')