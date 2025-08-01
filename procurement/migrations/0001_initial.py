# Generated by Django 5.2.4 on 2025-07-25 05:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0002_financialtransaction_payment_method_and_more'),
        ('sales', '0002_contact_notes_contact_performance_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
                ('quantity_on_hand', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('unit', models.CharField(default='pcs', max_length=20)),
                ('warehouse_location', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('po_id', models.CharField(max_length=50, unique=True)),
                ('status', models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('ordered', 'Ordered'), ('partially_received', 'Partially Received'), ('fully_received', 'Fully Received')], default='pending_approval', max_length=20)),
                ('order_date', models.DateField()),
                ('expected_delivery_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_orders', to='projects.project')),
                ('vendor', models.ForeignKey(limit_choices_to={'contact_type': 'supplier'}, on_delete=django.db.models.deletion.PROTECT, to='sales.contact')),
            ],
        ),
        migrations.CreateModel(
            name='GoodsReceivedNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grn_id', models.CharField(max_length=50, unique=True)),
                ('received_date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('received_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='grns', to='procurement.purchaseorder')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('unit', models.CharField(default='pcs', max_length=20)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='procurement.purchaseorder')),
            ],
        ),
        migrations.CreateModel(
            name='VendorInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(max_length=100)),
                ('invoice_date', models.DateField()),
                ('due_date', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved_for_payment', 'Approved for Payment'), ('paid', 'Paid')], default='pending_approval', max_length=30)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='vendor_invoices', to='procurement.purchaseorder')),
                ('vendor', models.ForeignKey(limit_choices_to={'contact_type': 'supplier'}, on_delete=django.db.models.deletion.PROTECT, to='sales.contact')),
            ],
        ),
    ]
