from flask import Blueprint
from crm.master.forms import MasterForm
from crm.models import Master
from crm import db, admin
from crm.hisaab.utils import cal_total_transfer
from crm.master.utils import cal_closing, cal_master_bal, cal_master_diff
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required


masters = Blueprint("master", __name__)


@masters.route("/home/master", methods=["GET", "POST"])
@login_required
def master():
    form = MasterForm()
    master = Master.query.order_by(Master.id.desc()).first()

    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)

        closing = cal_closing(form.opening.data, form.primary.data, total_trans)

        calc_master_bal = cal_master_bal(closing, form.fos_bal.data)

        master_diff = cal_master_diff(calc_master_bal, form.master_bal.data)

        master = Master(
            open_bal=form.opening.data,
            primary=form.primary.data,
            manual_trans=form.manual_trans.data,
            auto_trans=form.auto_trans.data,
            closing=closing,
            total_trans=total_trans,
            fos_bal=form.fos_bal.data,
            master_bal=form.master_bal.data,
            calc_master_bal=calc_master_bal,
            master_diff=master_diff,
            remarks=form.remarks.data,
        )

        db.session.add(master)
        db.session.commit()

        flash("Your report has been generated", "success")
        return redirect(url_for("master.master_report"))

    elif request.method == "GET":
        if master != None:
            form.opening.data = master.closing
        else:
            form.opening.data = 0

    return render_template(
        "master.html", title="Master", form=form, admin=admin, legend="Master Report"
    )


@masters.route("/home/master/master_report")
@login_required
def master_report():
    page = request.args.get("page", 1, type=int)
    master = Master.query.order_by(Master.date.desc()).paginate(page=page, per_page=5)
    return render_template(
        "master_report.html", title="Master Report", master=master, admin=admin
    )


@masters.route("/home/master/master_report/<int:master_id>")
@login_required
def single_master(master_id):
    if current_user.username != admin:
        abort(403)
    master = Master.query.get_or_404(master_id)
    return render_template(
        "single_master.html", title=master.date, master=master, admin=admin
    )


@masters.route(
    "/home/master/master_report/<int:master_id>/update", methods=["GET", "POST"]
)
@login_required
def update_master(master_id):
    master = Master.query.get_or_404(master_id)
    if current_user.username != admin:
        abort(403)
    form = MasterForm()
    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)

        closing = cal_closing(form.opening.data, form.primary.data, total_trans)

        calc_master_bal = cal_master_bal(closing, form.fos_bal.data)

        master_diff = cal_master_diff(calc_master_bal, form.master_bal.data)

        master.open_bal = form.opening.data
        master.date = datetime.now()
        master.primary = form.primary.data
        master.manual_trans = form.manual_trans.data
        master.auto_trans = form.auto_trans.data
        master.closing = closing
        master.total_trans = total_trans
        master.fos_bal = form.fos_bal.data
        master.master_bal = form.master_bal.data
        master.calc_master_bal = calc_master_bal
        master.master_diff = master_diff
        master.remarks = form.remarks.data

        db.session.commit()
        flash("Your master has been updated", "success")
        return redirect(url_for("master.single_master", master_id=master_id))
    elif request.method == "GET":
        form.opening.data = master.open_bal
        form.primary.data = master.primary
        form.manual_trans.data = master.manual_trans
        form.auto_trans.data = master.auto_trans
        form.fos_bal.data = master.fos_bal
        form.master_bal.data = master.master_bal
        form.remarks.data = master.remarks

    return render_template(
        "master.html",
        title="Update Master",
        form=form,
        admin=admin,
        master=master,
        legend="Update Master",
    )


@masters.route(
    "/home/master/master_report/<int:master_id>/delete", methods=["GET", "POST"]
)
@login_required
def delete_master(master_id):
    master = Master.query.get_or_404(master_id)
    if current_user.username != admin:
        abort(403)
    db.session.delete(master)
    db.session.commit()
    flash("Your master has been deleted!", "success")
    return redirect(url_for("master.master_report"))
