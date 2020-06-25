from datetime import datetime
from flask import Blueprint, flash, redirect, request, url_for, render_template, abort
from crm.hisaab.forms import HisaabForm
from crm.hisaab.utils import (
    cal_comm_value,
    cal_latest_debt,
    cal_net_sale,
    cal_total_sale,
    cal_total_transfer,
)
from crm.models import Hisaab, User
from flask_login import current_user, login_required
from crm import db, admin
from flask import flash


hisaabs = Blueprint("hisaab", __name__)


@hisaabs.route("/home/hisaab", methods=["GET", "POST"])
@login_required
def hisaab():
    form = HisaabForm()
    fos = User.query.filter_by(username=current_user.username).first()
    hisaab = Hisaab.query.filter_by(fos=fos).order_by(Hisaab.id.desc()).first()

    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)
        total_sale = cal_total_sale(
            (form.opening.data), total_trans, (form.closing.data)
        )
        comm_value = cal_comm_value(total_sale)
        net_sale = cal_net_sale(total_sale, comm_value)
        latest_debt = cal_latest_debt(
            net_sale, (form.last_debt.data), (form.amt_received.data)
        )

        hisaab = Hisaab(
            open_bal=form.opening.data,
            manual_trans=form.manual_trans.data,
            auto_trans=form.auto_trans.data,
            closing=form.closing.data,
            total_trans=total_trans,
            total_sale=total_sale,
            commission_value=comm_value,
            net_sale=net_sale,
            last_debt=form.last_debt.data,
            amt_received=form.amt_received.data,
            latest_debt=latest_debt,
            remarks=form.remarks.data,
            fos=current_user,
        )

        db.session.add(hisaab)
        db.session.commit()

        flash("Your report has been generated", "success")
        return redirect(url_for("users.user_hisaab", username=current_user.username))

    elif request.method == "GET":
        if hisaab != None:
            form.opening.data = hisaab.closing
            form.last_debt.data = hisaab.latest_debt
        else:
            form.opening.data = 0
            form.last_debt.data = 0

    return render_template(
        "hisaab.html", title="Hisaab", form=form, legend="New Hisaab"
    )


@hisaabs.route("/home/hisaab/report")
@login_required
def report():
    page = request.args.get("page", 1, type=int)
    hisaab = Hisaab.query.order_by(Hisaab.date.desc()).paginate(page=page, per_page=5)
    return render_template("report.html", title="Report", hisaab=hisaab, admin=admin)


@hisaabs.route("/home/hisaab/report/<int:hisaab_id>")
@login_required
def single_hisaab(hisaab_id):
    hisaab = Hisaab.query.get_or_404(hisaab_id)
    return render_template(
        "single_hisaab.html", title=hisaab.date, hisaab=hisaab, admin=admin
    )


@hisaabs.route("/home/hisaab/report/<int:hisaab_id>/update", methods=["GET", "POST"])
@login_required
def update_hisaab(hisaab_id):

    hisaab = Hisaab.query.get_or_404(hisaab_id)
    if current_user.username != admin:
        abort(403)
    form = HisaabForm()
    if form.validate_on_submit():

        total_trans = cal_total_transfer(form.manual_trans.data, form.auto_trans.data)
        total_sale = cal_total_sale(
            (form.opening.data), total_trans, (form.closing.data)
        )
        comm_value = cal_comm_value(total_sale)
        net_sale = cal_net_sale(total_sale, comm_value)
        latest_debt = cal_latest_debt(
            net_sale, (form.last_debt.data), (form.amt_received.data)
        )
        hisaab.date = datetime.now()
        hisaab.open_bal = form.opening.data
        hisaab.manual_trans = form.manual_trans.data
        hisaab.auto_trans = form.auto_trans.data
        hisaab.closing = form.closing.data
        hisaab.total_trans = total_trans
        hisaab.total_sale = total_sale
        hisaab.commission_value = comm_value
        hisaab.net_sale = net_sale
        hisaab.last_debt = form.last_debt.data
        hisaab.amt_received = form.amt_received.data
        hisaab.latest_debt = latest_debt
        hisaab.remarks = form.remarks.data
        db.session.commit()
        flash("Your hisaab has been updated", "success")
        return redirect(url_for("hisaab.single_hisaab", hisaab_id=hisaab_id))
    elif request.method == "GET":
        form.opening.data = hisaab.open_bal
        form.manual_trans.data = hisaab.manual_trans
        form.auto_trans.data = hisaab.auto_trans
        form.closing.data = hisaab.closing
        form.last_debt.data = hisaab.last_debt
        form.amt_received.data = hisaab.amt_received
        form.remarks.data = hisaab.remarks
    return render_template(
        "hisaab.html",
        title="Update Hisaab",
        hisaab=hisaab,
        admin=admin,
        form=form,
        legend="Update Hisaab",
    )


@hisaabs.route("/home/hisaab/report/<int:hisaab_id>/delete", methods=["POST"])
@login_required
def delete_hisaab(hisaab_id):
    hisaab = Hisaab.query.get_or_404(hisaab_id)
    if current_user.username != admin:
        abort(403)
    db.session.delete(hisaab)
    db.session.commit()
    flash("Your hisaab has been deleted!", "success")
    return redirect(url_for("hisaab.report"))
