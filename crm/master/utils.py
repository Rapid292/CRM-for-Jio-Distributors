def cal_closing(opening, primary, total_trans):
    closing = opening + primary - total_trans
    return closing


def cal_master_bal(closing, fos_bal):
    calc_master_bal = closing + fos_bal
    return calc_master_bal


def cal_master_diff(calc_master_bal, master_bal):
    diff = master_bal - calc_master_bal
    return diff

