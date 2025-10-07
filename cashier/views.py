from django.shortcuts import render, redirect, get_object_or_404
from common.models import Bill, Table, TaxSetting
from django.contrib.auth.decorators import login_required
from common.decorators import role_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO


@login_required
def cashier_dashboard(request):
    bills = Bill.objects.filter(is_paid=False).select_related('order__customer', 'order__table')
    return render(request, 'cashier/dashboard.html', {'bills': bills})

def view_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'cashier/view_bill.html', {'bill': bill, 'cgst': bill.cgst_amount(), 'sgst': bill.sgst_amount(), 'grand_total_with_tax': bill.grand_total_with_tax()})

def finalize_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    tax = TaxSetting.objects.last()

    if request.method == 'POST':
        method = request.POST.get('method')
        discount_str = request.POST.get('discount', '0')
        try:
            discount = float(discount_str) if discount_str.strip() else 0.0
        except ValueError:
            discount = 0.0

        # Calculate final total with tax and discount
        if tax:
            cgst_amount = float(bill.total) * float(tax.cgst) / 100.0
            sgst_amount = float(bill.total) * float(tax.sgst) / 100.0
        else:
            cgst_amount = 0.0
            sgst_amount = 0.0

        final_total = float(bill.total) + float(bill.tip) + cgst_amount + sgst_amount - discount

        bill.total = final_total
        bill.payment_method = method
        bill.is_paid = True
        bill.save()

        # Free the table
        table = bill.order.table
        table.is_occupied = False
        table.assigned_waiter = None
        table.save()

        return redirect('cashier_dashboard')

    return redirect('view_bill', bill_id=bill.id)


def generate_receipt(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    template = get_template('cashier/receipt_template.html')

    html = template.render({'bill': bill})
    response = BytesIO()

    pdf_status = pisa.CreatePDF(html, dest=response)
    if not pdf_status.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse("PDF generation error", status=500)

@login_required
def paid_bills(request):
    bills = Bill.objects.filter(is_paid=True).select_related('order__customer', 'order__table')
    return render(request, 'cashier/paid_bills.html', {'bills': bills})


def show_bill(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'cashier/show_bill.html', {'bill': bill, 'cgst': bill.cgst_amount(), 'sgst': bill.sgst_amount(), 'grand_total_with_tax': bill.grand_total_with_tax()})
