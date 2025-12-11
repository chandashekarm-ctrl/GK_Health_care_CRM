from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Customer
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import HospitalLead
from .models import PaymentFollowUp
from django.http import JsonResponse
from .models import Category
from .models import Product, Category
from .models import Product
from .models import Parts 
from .models import Employee
from .models import CustomerProduct
from .models import Customer
from datetime import datetime,timedelta
import os
from decimal import Decimal
from datetime import date, timedelta
from .models import Staff
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Quotation, QuotationItem, Category, Bank, TaxType
from .forms import QuotationForm, QuotationItemFormSet, QuotationSearchForm
from .models import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import HospitalLead, HospitalLeadParts, HospitalLeadProducts, Category, Product, Parts
import json
from django.shortcuts import render, redirect
from .models import Staff
from hr.models import Expense, EXPENSE_TYPES
from django.contrib.auth.decorators import user_passes_test

def edit_expense(request, id):
    expense = Expense.objects.get(id=id)

    if request.method == "POST":
        expense.staff_id = request.POST.get("staff")
        expense.expense_type = request.POST.get("expense_type")
        expense.amount = request.POST.get("amount")
        expense.description = request.POST.get("description")

        # Optional: Update Date if editable
        # expense.created_at = request.POST.get("created_at")

        expense.save()
        messages.success(request, "Expense updated successfully!")
        return redirect("staff_expense_list")

    return render(request, "edit_expense.html", {
        "expense": expense,
        "staff_list": Staff.objects.all(),
        "expense_types": EXPENSE_TYPES,
    })

def delete_expense(request, id):
    expense = Expense.objects.get(id=id)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect("staff_expense_list")

def add_staff_expense(request):
    staff_members = Staff.objects.all()

    if request.method == "POST":
        staff_id = request.POST.get("staff")
        expense_type = request.POST.get("expense_type")
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        remark = request.POST.get("remark")
        bill_image = request.FILES.get("bill_image")

        Expense.objects.create(
            staff_id=staff_id,
            expense_type=expense_type,
            amount=amount,
            description=description,
            remark=remark,
            bill_image=bill_image,
        )

        return redirect("staff_expense_list")

    return render(request, "add_staff_expense.html", {
        "staff": staff_members,
        "expense_types": EXPENSE_TYPES,
    })

from django.db.models import Sum
from datetime import datetime

def staff_expense_list(request):

    expenses = Expense.objects.select_related("staff").order_by("-created_at")

    staff_id = request.GET.get("staff")
    exp_type = request.GET.get("type")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    # Apply Staff Filter
    if staff_id:
        expenses = expenses.filter(staff_id=staff_id)

    # Apply Type Filter
    if exp_type:
        expenses = expenses.filter(expense_type=exp_type)

    # Apply Date Range Filter
    if from_date:
        expenses = expenses.filter(created_at__date__gte=from_date)

    if to_date:
        expenses = expenses.filter(created_at__date__lte=to_date)

    # Calculate Total
    total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or 0

    return render(request, "staff_expense_list.html", {
        "expenses": expenses,
        "staff_list": Staff.objects.all(),
        "expense_types": EXPENSE_TYPES,

        # Selected
        "selected_staff": staff_id,
        "selected_type": exp_type,
        "selected_from": from_date,
        "selected_to": to_date,

        # Total
        "total_expenses": total_expenses,
    })

def payment_followup_form(request):
    return render(request, 'payment_followup_form.html')

def save_payment_followup(request):
    if request.method == 'POST':
        try:
            PaymentFollowUp.objects.create(
                client_name=request.POST.get('client_name'),
                amount=request.POST.get('amount'),
                mode_of_payment=request.POST.get('mode_of_payment'),
                payment_status=request.POST.get('payment_status'),
                follow_up_date=request.POST.get('follow_up_date'),
                next_follow_date=request.POST.get('next_follow_date'),
                last_payment_date=request.POST.get('last_payment_date'),
                due_days=request.POST.get('due_days'),
                present_date=request.POST.get('present_date')
            )
            messages.success(request, 'Payment follow-up details saved successfully!')
            return redirect('payment_followup_form')
        except Exception as e:
            messages.error(request, f'Error saving data: {str(e)}')
            return redirect('payment_followup_form')
    return redirect('payment_followup_form')

from .models import user_password

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import user_password

def login_view(request):
    users = user_password.objects.all()

    MASTER_PASSWORD = "Crm#1234"   # <<< Set Your Password Here

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check Master Password
        if password != MASTER_PASSWORD:
            return render(request, 'login.html', {
                'error': 'Invalid master password!',
                'users': users
            })

        # Django authentication
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

        # Custom DB authentication but master password is required
        elif user_password.objects.filter(user=username).exists():
            request.session['username'] = username
            return redirect('dashboard')

        else:
            return render(request, 'login.html', {
                'error': 'Invalid username!',
                'users': users
            })

    return render(request, 'login.html', {'users': users})

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    expenses = Expense.objects.select_related("staff").order_by("-created_at")
    total_expenses = expenses.aggregate(total=Sum("amount"))["total"] or 0
    total_customers = Customer.objects.count()
    total_vendors = Vendor.objects.count()
    total_leads = HospitalLead.objects.count()
    total_tasks = TaskAssign.objects.count()
    total_products = Product.objects.count()
    total_customers = HospitalLead.objects.filter(lead_source="Customer").count()

    context = {
        "total_customers": total_customers,
        "total_vendors": total_vendors,
        "total_leads": total_leads,
        "total_tasks": total_tasks,
        "total_products": total_products,
        'total_expenses':total_expenses,
        
    }
    return render(request, "dashboard.html", context)

def payment(request):
    return render(request, 'payment.html')

def new_lead(request):
    if request.method == 'POST':
        try:
            # Create HospitalLead instance
            lead = HospitalLead()
            
            # Basic hospital information
            lead.hospital_name = request.POST.get('hospital_name')
            hospital_type = request.POST.get('hospital_type')
            if hospital_type == 'Other':
                lead.hospital_type = request.POST.get('hospital_type_other', 'Other')
            else:
                lead.hospital_type = hospital_type
            lead.lead_source = request.POST.get('lead_source', 'Customer')

            # Contact information
            lead.first_name = request.POST.get('first_name')
            lead.last_name = request.POST.get('last_name')
            lead.phone = request.POST.get('phone')
            lead.email = request.POST.get('email')
            lead.address = request.POST.get('address')
            lead.city = request.POST.get('city')
            lead.state = request.POST.get('state')
            lead.country = request.POST.get('country', 'India')
            
            # Decision maker information (handle multiple selections)
            decision_makers = request.POST.getlist('decision_maker')
            if 'Other' in decision_makers:
                other_decision = request.POST.get('decision_maker_other')
                if other_decision:
                    decision_makers.remove('Other')
                    decision_makers.append(other_decision)
            lead.decision_maker = decision_makers
            
            # Telecalling response (handle multiple selections)
            telecalling_responses = request.POST.getlist('telecalling_response')
            if 'Other' in telecalling_responses:
                other_response = request.POST.get('telecalling_response_other')
                if other_response:
                    telecalling_responses.remove('Other')
                    telecalling_responses.append(other_response)
            lead.telecalling_response = telecalling_responses
            
            # Follow-up information
            followup_date = request.POST.get('followup_date')
            followup_time = request.POST.get('followup_time')
            lead.followup_date = followup_date if followup_date else None
            lead.followup_time = followup_time if followup_time else None
            
            # Communication preferences
            lead.communication_channel = request.POST.get('communication_channel')
            lead.promotional_messages = request.POST.get('promotional_messages')
            lead.remarks = request.POST.get('remarks')
            
            # Set created_by to current user
            lead.created_by = request.user
            
            # Save the lead first
            lead.save()
            
            # Handle products
            product_data = {}
            for key, value in request.POST.items():
                if key.startswith('products[') and value:
                    # Extract index and field from key like 'products[0][id]'
                    import re
                    match = re.match(r'products\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index, field = match.groups()
                        if index not in product_data:
                            product_data[index] = {}
                        product_data[index][field] = value
            
            # Save selected products
            for product_info in product_data.values():
                product_id = product_info.get('id')
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        HospitalLeadProducts.objects.get_or_create(
                            hospital_lead=lead,
                            product=product
                        )
                    except Product.DoesNotExist:
                        messages.warning(request, f'Product with ID {product_id} not found')
            
            # Handle parts
            parts_data = {}
            for key, value in request.POST.items():
                if key.startswith('parts[') and value:
                    # Extract index and field from key like 'parts[0][id]'
                    import re
                    match = re.match(r'parts\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index, field = match.groups()
                        if index not in parts_data:
                            parts_data[index] = {}
                        parts_data[index][field] = value
            
            # Save selected parts
            for parts_info in parts_data.values():
                part_id = parts_info.get('id')
                if part_id:
                    try:
                        part = Parts.objects.get(id=part_id)
                        HospitalLeadParts.objects.get_or_create(
                            hospital_lead=lead,
                            part=part
                        )
                    except Parts.DoesNotExist:
                        messages.warning(request, f'Part with ID {part_id} not found')
            
            messages.success(request, 'Hospital lead created successfully!')
            return redirect('hospital_leads_list')  # Redirect to leads list page
            
        except Exception as e:
            messages.error(request, f'Error creating lead: {str(e)}')
            return render(request, 'new_lead.html', get_form_context())
    
    else:
        return render(request, 'new_lead.html', get_form_context())

def get_form_context():
    """Helper function to get context data for the form"""
    # Get categories grouped by ID
    categories = {}
    for category in Category.objects.all():
        if category.id not in categories:
            categories[category.id] = []
        categories[category.id].append(category)
    
    context = {
        'categories': categories,
        'products': Product.objects.all(),
        'parts': Parts.objects.all(),
    }
    return context

from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from .models import HospitalLead
from django.views.decorators.http import require_GET

def hospital_leads_list(request):
    """
    Show ALL hospital leads (Lead + Customer) with filters:
    - hospital
    - lead_source (All / Customer / Lead)
    - city
    - state
    - free-text search 'q'
    """

    # --- Base queryset (ALL leads) ---
    leads = HospitalLead.objects.all().prefetch_related(
        'lead_parts__part',
        'lead_products__product'
    ).order_by('-created_at')

    # --- Get filter params ---
    hospital_filter = request.GET.get('hospital', '').strip()
    city_filter = request.GET.get('city', '').strip()
    state_filter = request.GET.get('state', '').strip()
    lead_source_filter = request.GET.get('lead_source', '').strip()
    search_query = request.GET.get('q', '').strip()

    # --- Apply filters ---
    if hospital_filter:
        leads = leads.filter(id=hospital_filter)

    if lead_source_filter:
        leads = leads.filter(lead_source=lead_source_filter)

    if city_filter:
        leads = leads.filter(city__iexact=city_filter)

    if state_filter:
        leads = leads.filter(state__iexact=state_filter)

    if search_query:
        leads = leads.filter(
            Q(hospital_name__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(state__icontains=search_query)
        )

    # --- For dropdowns (ALL leads, not filtered, or you can use distinct over full table) ---
    base_queryset = HospitalLead.objects.all()

    hospitals = base_queryset.order_by('hospital_name')

    cities = sorted(set(
        c.strip().title()
        for c in base_queryset.values_list('city', flat=True)
        if c
    ))

    states = sorted(set(
        s.strip().title()
        for s in base_queryset.values_list('state', flat=True)
        if s
    ))

    total_leads = base_queryset.count()

    context = {
        'leads': leads,
        'hospitals': hospitals,
        'cities': cities,
        'states': states,
        'total_leads': total_leads,

        # Keep selected values for UI
        'selected_hospital': hospital_filter,
        'selected_city': city_filter,
        'selected_state': state_filter,
        'selected_lead_source': lead_source_filter,
        'search_query': search_query,
    }

    return render(request, 'hospital_leads_list.html', context)

@require_GET
def get_cities(request):
    """
    Return cities for a given state (for dropdown).
    URL: /get-cities/?state=Karnataka
    """
    state = request.GET.get('state', '').strip()
    if not state:
        return JsonResponse({'cities': []})

    qs = HospitalLead.objects.filter(state__iexact=state).values_list('city', flat=True)
    cities = sorted(set(
        c.strip().title()
        for c in qs if c
    ))
    return JsonResponse({'cities': cities})

@require_GET
def get_hospitals(request):
    """
    Return hospitals for a given city (for dropdown).
    URL: /get-hospitals/?city=Bengaluru
    """
    city = request.GET.get('city', '').strip()
    if not city:
        return JsonResponse({'hospitals': []})

    qs = HospitalLead.objects.filter(city__iexact=city).order_by('hospital_name')
    hospitals = [
        {
            'id': h.id,
            'hospital_name': h.hospital_name,
            'city': h.city or ''
        }
        for h in qs
    ]
    return JsonResponse({'hospitals': hospitals})

def hospital_lead_detail(request, lead_id):
    """View to display detailed information about a specific lead"""
    lead = get_object_or_404(HospitalLead, id=lead_id)
    lead_parts = HospitalLeadParts.objects.filter(hospital_lead=lead)
    lead_products = HospitalLeadProducts.objects.filter(hospital_lead=lead)
    
    context = {
        'lead': lead,
        'lead_parts': lead_parts,
        'lead_products': lead_products,
    }
    return render(request, 'hospital_lead_detail.html', context)
    
def hospital_lead_edit(request, pk):
    lead = get_object_or_404(HospitalLead, pk=pk)
    
    if request.method == 'POST':
        try:
            # Basic hospital information
            lead.hospital_name = request.POST.get('hospital_name')
            hospital_type = request.POST.get('hospital_type')
            if hospital_type == 'Other':
                lead.hospital_type = request.POST.get('hospital_type_other', 'Other')
            else:
                lead.hospital_type = hospital_type
            
            # Contact information
            lead.first_name = request.POST.get('first_name')
            lead.last_name = request.POST.get('last_name')
            lead.designation = request.POST.get('designation')
            lead.phone = request.POST.get('phone')
            lead.email = request.POST.get('email')
            lead.address = request.POST.get('address')
            lead.city = request.POST.get('city')
            lead.state = request.POST.get('state')
            lead.country = request.POST.get('country', 'India')
            lead.lead_source = request.POST.get('lead_source')
            # Decision maker information (handle multiple selections)
            decision_makers = request.POST.getlist('decision_maker')
            if 'Other' in decision_makers:
                other_decision = request.POST.get('decision_maker_other')
                if other_decision:
                    decision_makers.remove('Other')
                    decision_makers.append(other_decision)
            lead.decision_maker = decision_makers
            
            # Telecalling response (handle multiple selections)
            telecalling_responses = request.POST.getlist('telecalling_response')
            if 'Other' in telecalling_responses:
                other_response = request.POST.get('telecalling_response_other')
                if other_response:
                    telecalling_responses.remove('Other')
                    telecalling_responses.append(other_response)
            lead.telecalling_response = telecalling_responses
            
            # Category information
            lead.category_id = request.POST.get('category_id')
            lead.category_name = request.POST.get('category_name')
            
            # Follow-up information
            followup_date = request.POST.get('followup_date')
            followup_time = request.POST.get('followup_time')
            lead.followup_date = followup_date if followup_date else None
            lead.followup_time = followup_time if followup_time else None
            
            # Communication preferences
            lead.communication_channel = request.POST.get('communication_channel')
            lead.promotional_messages = request.POST.get('promotional_messages')
            lead.remarks = request.POST.get('remarks')
            
            # Save the lead first
            lead.save()
            
            # Handle products - Delete existing and add new ones
            HospitalLeadProducts.objects.filter(hospital_lead=lead).delete()
            
            product_data = {}
            for key, value in request.POST.items():
                if key.startswith('products[') and value:
                    # Extract index and field from key like 'products[0][id]'
                    import re
                    match = re.match(r'products\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index, field = match.groups()
                        if index not in product_data:
                            product_data[index] = {}
                        product_data[index][field] = value
            
            # Save selected products
            for product_info in product_data.values():
                product_id = product_info.get('id')
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        HospitalLeadProducts.objects.get_or_create(
                            hospital_lead=lead,
                            product=product
                        )
                    except Product.DoesNotExist:
                        messages.warning(request, f'Product with ID {product_id} not found')
            
            # Handle parts - Delete existing and add new ones
            HospitalLeadParts.objects.filter(hospital_lead=lead).delete()
            
            parts_data = {}
            for key, value in request.POST.items():
                if key.startswith('parts[') and value:
                    # Extract index and field from key like 'parts[0][id]'
                    import re
                    match = re.match(r'parts\[(\d+)\]\[(\w+)\]', key)
                    if match:
                        index, field = match.groups()
                        if index not in parts_data:
                            parts_data[index] = {}
                        parts_data[index][field] = value
            
            # Save selected parts
            for parts_info in parts_data.values():
                part_id = parts_info.get('id')
                if part_id:
                    try:
                        part = Parts.objects.get(id=part_id)
                        HospitalLeadParts.objects.get_or_create(
                            hospital_lead=lead,
                            part=part
                        )
                    except Parts.DoesNotExist:
                        messages.warning(request, f'Part with ID {part_id} not found')
            
            messages.success(request, 'Hospital lead updated successfully!')
            return redirect('hospital_leads_list')  # Redirect to leads list page
            
        except Exception as e:
            messages.error(request, f'Error updating lead: {str(e)}')
            return render(request, 'hospital_lead_edit.html', get_edit_form_context(lead))
    
    else:
        return render(request, 'hospital_lead_edit.html', get_edit_form_context(lead))

def get_edit_form_context(lead):
    """Helper function to get context data for the edit form"""
    from .models import Category, Product, Parts, HospitalLeadProducts, HospitalLeadParts
    
    # Preprocess decision makers and telecalling responses for template
    dm_list = lead.decision_maker if isinstance(lead.decision_maker, list) else []
    telecalling_list = lead.telecalling_response if isinstance(lead.telecalling_response, list) else []
    
    # Get all categories - create the structure expected by template
    categories = {}
    all_categories = Category.objects.all()
    for category in all_categories:
        categories[category.id] = [{'id': category.id, 'name': category.name}]
    
    # Get all products and parts
    products = Product.objects.all()
    parts = Parts.objects.all()
    
    # Get existing products and parts for this lead
    lead_products = HospitalLeadProducts.objects.filter(hospital_lead=lead).select_related('product')
    lead_parts = HospitalLeadParts.objects.filter(hospital_lead=lead).select_related('part')
    
    # Options for decision makers
    decision_maker_options = [
        "Dialysis Technician", "Nephrologist", "Purchase Department",
        "Account Department", "Biomedical Department", "store", "owner", "Other"
    ]
    
    return {
        "lead": lead,
        "dm_list": dm_list,
        "telecalling_list": telecalling_list,
        "decision_maker_options": decision_maker_options,
        "categories": categories,
        "products": products,
        "parts": parts,
        "lead_products": lead_products,
        "lead_parts": lead_parts,
    }

def delete_hospital_lead(request, pk):
    lead = get_object_or_404(HospitalLead, pk=pk)

    if request.method == "POST":
        lead.delete()
        messages.success(request, "Hospital Lead deleted successfully.")
        return redirect(reverse("hospital_leads_list"))

    return render(request, "delete_hospital_lead_confirm.html", {"lead": lead})

def add_category(request):
    return render(request, 'add_categories.html')

def save_category(request):
    if request.method == 'POST':
        try:
            Category.objects.create(
                id=request.POST.get('category_id'),
                name=request.POST.get('category_name'),
                description=request.POST.get('description'),
                image=request.FILES.get('category_image')
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'update_categories.html', {'category': category})

def save_updated_category(request, category_id):
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=request.POST.get('category_id_original'))
            category.id = request.POST.get('category_id')
            category.name = request.POST.get('category_name')
            category.description = request.POST.get('description')
            
            if 'category_image' in request.FILES:
                category.image = request.FILES.get('category_image')
            
            category.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def delete_category(request, category_id):
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def category_list(request):
    categories = Category.objects.all()
    
    # Create paginator with 10 items per page
    paginator = Paginator(categories, 5)

    # Get the page number from request
    page_number = request.GET.get('page')

    # Get the page object
    page_obj = paginator.get_page(page_number)

    return render(request, 'category_list.html', {'page_obj': page_obj})

def add_category(request):
    if request.method == 'POST':
        Category.objects.create(
            id=request.POST['category_id'],
            name=request.POST['category_name']
        )
        return redirect('category_list')
    return render(request, 'add_category.html')

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        try:
            category.id = request.POST['category_id']
            category.name = request.POST['category_name']
            # Save other fields as needed
            category.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return render(request, 'edit_category.html', {'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('category_list')

def product(request):
    products = Product.objects.all()
    if request.method == 'POST':
        # Handle multiple products
        products_data = []
        for key, value in request.POST.items():
            if key.startswith('products[') and key.endswith('][id]'):
                index = key.split('[')[1].split(']')[0]
                product_id = value
                product_name = request.POST.get(f'products[{index}][name]', '')
                if product_id and product_name:
                    products_data.append({
                        'id': product_id,
                        'name': product_name
                    })
        
        # Process your lead with products_data here
        print("Received products:", products_data)
        
    return render(request, 'new_lead.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    
    # Create paginator with 5 items per page
    paginator = Paginator(products, 5)
    
    # Get the page number from request
    page_number = request.GET.get('page')
    
    # Get the page object
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'product_list.html', {'page_obj': page_obj})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

def add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            id=request.POST.get('product_id'),
            name=request.POST.get('product_name'),
            selling_price=request.POST.get('selling_price'),
            tax_percent=request.POST.get('tax_percent'),
            purchase_price=request.POST.get('purchase_price'),
            unit=request.POST.get('product_unit'),
            hsn_sac=request.POST.get('hsn_sac'),
            description=request.POST.get('description'),
            category_id=request.POST.get('category_id'),
            product_image=request.FILES.get('product_image')
        )
        return redirect('product_list')
    
    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})
    
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            # Helper function to handle decimal fields
            def get_decimal_value(field_name, default_value):
                value = request.POST.get(field_name, '').strip()
                if value == '' or value is None:
                    return default_value
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default_value
            
            # Update product fields with proper validation
            product.name = request.POST.get('name', '').strip() or product.name
            
            # Handle decimal fields safely
            product.selling_price = get_decimal_value('selling_price_with_tax', product.selling_price)
            product.tax_percent = get_decimal_value('tax_percentage', product.tax_percent)
            product.purchase_price = get_decimal_value('purchase_price_with_tax', product.purchase_price)
            
            # Handle text fields
            product.unit = request.POST.get('unit', product.unit)
            product.hsn_sac = request.POST.get('hsn_sac', '').strip() or product.hsn_sac
            product.description = request.POST.get('description', '').strip() or product.description
            
            # Handle category
            category_id = request.POST.get('category')
            if category_id:
                product.category_id = category_id

            # Handle image upload (check both possible field names)
            if 'image' in request.FILES:
                if hasattr(product, 'image'):
                    product.image = request.FILES['image']
                elif hasattr(product, 'product_image'):
                    product.product_image = request.FILES['image']
            
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('edit_product', product_id=product_id)
    
    # Get all categories for the dropdown
    categories = Category.objects.all()
    return render(request, 'edit_product.html', {
        'product': product, 
        'categories': categories
    })

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, f'Product "{product.name}" deleted successfully!')
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('product_list')
    
    # For GET request, show confirmation page
    return render(request, 'delete_product_confirm.html', {'product': product})

def parts_list(request):
    parts_list = Parts.objects.all()
    
    # Create paginator with 5 items per page
    paginator = Paginator(parts_list, 5)
    
    # Get the page number from request
    page_number = request.GET.get('page')
    
    # Get the page object
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'parts_list.html', {'page_obj': page_obj})

def parts_detail(request, parts_id):
    parts = get_object_or_404(Parts, id=parts_id)
    return render(request, 'parts_detail.html', {'parts': parts})

def add_parts(request):
    if request.method == 'POST':
        try:
            # Get category and product objects if provided
            category = None
            product = None
            
            category_id = request.POST.get('category')
            if category_id:
                category = get_object_or_404(Category, id=category_id)
            
            product_id = request.POST.get('product')
            if product_id:
                product = get_object_or_404(Product, id=product_id)
            
            # Create the parts object
            Parts.objects.create(
                id=request.POST.get('parts_id'),
                name=request.POST.get('parts_name'),
                category=category,
                product=product,
                description=request.POST.get('description', '').strip() or None,
                parts_image=request.FILES.get('parts_image')
            )
            messages.success(request, 'Parts added successfully!')
            return redirect('parts_list')
        except Exception as e:
            messages.error(request, f'Error adding parts: {str(e)}')
    
    # Get categories and products for the form
    categories = Category.objects.all()
    products = Product.objects.all()
    
    return render(request, 'add_parts.html', {
        'categories': categories,
        'products': products
    })

def edit_parts(request, parts_id):
    parts = get_object_or_404(Parts, id=parts_id)
    
    if request.method == 'POST':
        try:
            # Update parts fields
            parts.name = request.POST.get('name', '').strip() or parts.name
            parts.description = request.POST.get('description', '').strip() or None
            
            # Handle category selection
            category_id = request.POST.get('category')
            if category_id:
                parts.category = get_object_or_404(Category, id=category_id)
            else:
                parts.category = None
            
            # Handle product selection
            product_id = request.POST.get('product')
            if product_id:
                parts.product = get_object_or_404(Product, id=product_id)
            else:
                parts.product = None
            
            # Handle image upload (check both possible field names)
            if 'image' in request.FILES:
                if hasattr(parts, 'image'):
                    parts.image = request.FILES['image']
                elif hasattr(parts, 'parts_image'):
                    parts.parts_image = request.FILES['image']
            
            parts.save()
            messages.success(request, 'Parts updated successfully!')
            return redirect('parts_list')
            
        except Exception as e:
            messages.error(request, f'Error updating parts: {str(e)}')
            return redirect('edit_parts', parts_id=parts_id)
    
    # Get categories and products for the form
    categories = Category.objects.all()
    products = Product.objects.all()
    
    return render(request, 'edit_parts.html', {
        'parts': parts,
        'categories': categories,
        'products': products
    })

def delete_parts(request, parts_id):
    parts = get_object_or_404(Parts, id=parts_id)
    
    if request.method == 'POST':
        try:
            parts.delete()
            messages.success(request, f'Parts "{parts.name}" deleted successfully!')
            return redirect('parts_list')
        except Exception as e:
            messages.error(request, f'Error deleting parts: {str(e)}')
            return redirect('parts_list')
    
    # For GET request, show parts list
    return redirect('parts_list')

def add_customer(request):
    """Display the add customer form"""
    return render(request, 'add_customer.html')
 
def save_customer(request):
    """Save customer data to database"""
    if request.method == 'POST':
        try:
            customer = Customer.objects.create(
                customer_id=request.POST.get('customer_id', '').strip() or None,
                company_name=request.POST.get('company_name', '').strip() or None,
                customer_name=request.POST.get('customer_name', '').strip(),
                phone_number=request.POST.get('phone_number', '').strip(),
                phone_number_2=request.POST.get('phone_number_2', '').strip() or None,
                email=request.POST.get('email', '').strip() or None,
                gstin=request.POST.get('gstin', '').strip() or None,
                address_line_1=request.POST.get('address_line_1', '').strip() or None,
                address_line_2=request.POST.get('address_line_2', '').strip() or None,
                city=request.POST.get('city', '').strip() or None,
                state=request.POST.get('state', '').strip() or None,
                pincode=request.POST.get('pincode', '').strip() or None,
                company_website=request.POST.get('company_website', '').strip() or None,
                created_by=request.user,
            )
            messages.success(request, f'Customer "{customer.customer_name}" added successfully!')
            return redirect('customer_list')  # or use 'total_customer' if separate view

        except Exception as e:
            messages.error(request, f'Error adding customer: {str(e)}')
            return redirect('add_customer')

    return redirect('add_customer')

@user_passes_test(lambda u: u.is_superuser)
def customer_list(request):
    """Display only CUSTOMER leads with filters."""

    # Base queryset → ONLY CUSTOMERS
    base_queryset = HospitalLead.objects.filter(
        lead_source="Customer"
    ).order_by('-created_at')

    # Get Filters
    selected_hospital = request.GET.get("hospital")
    selected_city = request.GET.get("city")
    selected_state = request.GET.get("state")
    search_term = request.GET.get("q", "").strip()

    hospital_leads = base_queryset  # Start with all customers

    # Apply State Filter
    if selected_state:
        hospital_leads = hospital_leads.filter(state__iexact=selected_state)

    # Apply City Filter
    if selected_city:
        hospital_leads = hospital_leads.filter(city__iexact=selected_city)

    # Apply Hospital Filter
    if selected_hospital:
        hospital_leads = hospital_leads.filter(id=selected_hospital)

    # Apply Search Filter
    if search_term:
        hospital_leads = hospital_leads.filter(
            Q(hospital_name__icontains=search_term) |
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term) |
            Q(city__icontains=search_term) |
            Q(state__icontains=search_term)
        )

    # Dropdown lists depend on state/city filters
    # States always from all customers
    states = sorted(set(
        base_queryset.values_list("state", flat=True)
    ))

    # Cities depend on selected_state
    if selected_state:
        cities = sorted(set(
            base_queryset.filter(state=selected_state).values_list("city", flat=True)
        ))
    else:
        cities = sorted(set(base_queryset.values_list("city", flat=True)))

    # Hospitals depend on selected_city
    if selected_city:
        hospitals = base_queryset.filter(city=selected_city)
    else:
        hospitals = base_queryset

    return render(request, "customer_list_1.html", {
        "hospital_leads": hospital_leads,
        "hospitals": hospitals,
        "states": states,
        "cities": cities,
        "total_customers": base_queryset.count(),

        # Selected filters for UI
        "selected_state": selected_state,
        "selected_city": selected_city,
        "selected_hospital": selected_hospital,
        "search_term": search_term,
    })

def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    employees = customer.employees.all()  # Uses related_name='employees' from Employee model
    customer_products = customer.products.all()  # Assuming you have a CustomerProduct model

    return render(request, 'customer_detail.html', {
        'customer': customer,
        'employees': employees,
        'customer_products': customer_products
    })

def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        try:
            customer.company_name = request.POST.get('company_name', '').strip() or None
            customer.customer_name = request.POST.get('customer_name', '').strip()
            customer.phone_number = request.POST.get('phone_number', '').strip()
            customer.phone_number_2 = request.POST.get('phone_number_2', '').strip() or None
            customer.email = request.POST.get('email', '').strip() or None
            customer.gstin = request.POST.get('gstin', '').strip() or None
            customer.address_line_1 = request.POST.get('address_line_1', '').strip() or None
            customer.address_line_2 = request.POST.get('address_line_2', '').strip() or None
            customer.city = request.POST.get('city', '').strip() or None
            customer.state = request.POST.get('state', '').strip() or None
            customer.pincode = request.POST.get('pincode', '').strip() or None
            customer.company_website = request.POST.get('company_website', '').strip() or None

            customer.save()
            messages.success(request, f'Customer "{customer.customer_name}" updated successfully!')
            return redirect('customer_detail', customer_id=customer.id)

        except Exception as e:
            messages.error(request, f'Error updating customer: {str(e)}')
            return redirect('edit_customer', customer_id=customer_id)

    return render(request, 'edit_customer.html', {'customer': customer})

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        try:
            customer_name = customer.customer_name
            customer.delete()
            messages.success(request, f'Customer "{customer_name}" deleted successfully!')
            return redirect('customer_list')
        except Exception as e:
            messages.error(request, f'Error deleting customer: {str(e)}')
            return redirect('customer_list')

    return render(request, 'delete_customer.html', {'customer': customer})

def add_employee(request, customer_id):
    """Add new employee linked to a customer"""
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        try:
            position = request.POST.get('position')
            name = request.POST.get('employee_name')  # match with form field
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            date_of_birth = request.POST.get('date_of_birth')

            if not all([position, name, phone_number, email, date_of_birth]):
                messages.error(request, 'All fields are required!')
                return render(request, 'add_employee.html', {'customer': customer})

            Employee.objects.create(
                customer=customer,  # Assuming you have a ForeignKey to Customer in Employee model
                position=position,
                name=name,
                phone_number=phone_number,
                email=email,
                date_of_birth=date_of_birth
            )

            messages.success(request, f'Employee {name} added successfully!')
            return redirect('customer_detail', customer_id=customer.id)

        except Exception as e:
            messages.error(request, f'Error adding employee: {str(e)}')
            return render(request, 'add_employee.html', {'customer': customer})

    return render(request, 'add_employee.html', {'customer': customer})

def edit_employee(request, employee_id):
    """Edit existing employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    customer_id = employee.customer.id  # Assuming Employee has a ForeignKey to Customer

    if request.method == 'POST':
        try:
            employee.position = request.POST.get('position')
            employee.name = request.POST.get('employee_name')
            employee.phone_number = request.POST.get('phone_number')
            employee.email = request.POST.get('email')
            employee.date_of_birth = request.POST.get('date_of_birth')
            employee.save()

            messages.success(request, f'Employee {employee.name} updated successfully!')
            return redirect('customer_detail', customer_id=customer_id)

        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')

    return render(request, 'edit_employee.html', {
        'employee': employee,
        'customer': employee.customer,
        'is_edit': True
    })

def delete_employee(request, employee_id):
    """Delete employee"""
    employee = get_object_or_404(Employee, id=employee_id)
    customer_id = employee.customer.id

    if request.method == 'POST':
        try:
            employee_name = employee.name
            employee.delete()
            messages.success(request, f'Employee {employee_name} deleted successfully!')
            return redirect('customer_detail', customer_id=customer_id)
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
            return redirect('customer_detail', customer_id=customer_id)

    return render(request, 'delete_employee.html', {'employee': employee})

def add_customer_product(request, customer_id):
   customer = get_object_or_404(Customer, id=customer_id)
   categories = Category.objects.all()  # Assuming you have a Category model
   
   if request.method == 'POST':
       # Create the product
       product = CustomerProduct.objects.create(
           customer=customer,
           product_id=request.POST.get('product_id'),
           product_name=request.POST.get('product_name'),
           manufacturer=request.POST.get('manufacturer') or None,
           serial_number=request.POST.get('serial_number') or None,
           selling_price=request.POST.get('selling_price'),
           purchase_price=request.POST.get('purchase_price') or None,
           installation_date=request.POST.get('installation_date') or None,
           warranty_period_date=request.POST.get('warranty_period_date') or None,
           tax_percent=request.POST.get('tax_percent') or None,
           product_unit=request.POST.get('product_unit'),
           hsn_sac=request.POST.get('hsn_sac'),
           category_id=request.POST.get('category_id') or None,
           description=request.POST.get('description'),
       )
       
       # Handle image upload
       if request.FILES.get('product_image'):
           product.product_image = request.FILES['product_image']
           product.save()
       
       messages.success(request, f'Product "{product.product_name}" added successfully!')
       return redirect('customer_detail', customer_id=customer.id)
   
   context = {
       'customer': customer,
       'categories': categories,
   }
   return render(request, 'add_customer_product.html', context)

def edit_customer_product(request, product_id):
   product = get_object_or_404(CustomerProduct, id=product_id)
   customer = product.customer
   categories = Category.objects.all()
   
   if request.method == 'POST':
       # Update product fields
       product.product_id = request.POST.get('product_id')
       product.product_name = request.POST.get('product_name')
       product.manufacturer = request.POST.get('manufacturer') or None
       product.serial_number = request.POST.get('serial_number') or None
       product.installation_date = request.POST.get('installation_date') or None
       product.warranty_period_date = request.POST.get('warranty_period_date') or None
       product.selling_price = request.POST.get('selling_price')
       product.purchase_price = request.POST.get('purchase_price') or None
       product.tax_percent = request.POST.get('tax_percent') or None
       product.product_unit = request.POST.get('product_unit')
       product.hsn_sac = request.POST.get('hsn_sac')
       product.category_id = request.POST.get('category_id') or None
       product.description = request.POST.get('description')
       
       # Handle image upload
       if request.FILES.get('product_image'):
           product.product_image = request.FILES['product_image']
       
       product.save()
       messages.success(request, f'Product "{product.product_name}" updated successfully!')
       return redirect('customer_detail', customer_id=customer.id)
   
   context = {
       'customer': customer,
       'product': product,
       'categories': categories,
   }
   return render(request, 'edit_customer_product.html', context)

def delete_customer_product(request, product_id):
   product = get_object_or_404(CustomerProduct, id=product_id)
   customer_id = product.customer.id
   product_name = product.product_name
   
   # Delete the product image file if it exists
   if product.product_image:
       if os.path.isfile(product.product_image.path):
           os.remove(product.product_image.path)
   
   product.delete()
   messages.success(request, f'Product "{product_name}" deleted successfully!')
   return redirect('customer_detail', customer_id=customer_id)

from .models import Vendor, VendorEmployee, VendorProduct

def add_vendor(request):
    """Display the add vendor form"""
    return render(request, 'add_vendor.html')

def save_vendor(request):
    """Save vendor data to database"""
    if request.method == 'POST':
        try:
            vendor = Vendor.objects.create(
                vendor_id=request.POST.get('vendor_id', '').strip(),
                company_name=request.POST.get('company_name', '').strip() or None,
                vendor_name=request.POST.get('vendor_name', '').strip(),
                phone_number=request.POST.get('phone_number', '').strip(),
                phone_number_2=request.POST.get('phone_number_2', '').strip() or None,
                email=request.POST.get('email', '').strip() or None,
                gstin=request.POST.get('gstin', '').strip() or None,
                address_line_1=request.POST.get('address_line_1', '').strip() or None,
                address_line_2=request.POST.get('address_line_2', '').strip() or None,
                city=request.POST.get('city', '').strip() or None,
                state=request.POST.get('state', '').strip() or None,
                pincode=request.POST.get('pincode', '').strip() or None,
                company_website=request.POST.get('company_website', '').strip() or None,
                created_by=request.user,
            )
            messages.success(request, f'Vendor "{vendor.vendor_name}" added successfully!')
            return redirect('vendor_list')

        except Exception as e:
            messages.error(request, f'Error adding vendor: {str(e)}')
            return redirect('add_vendor')

    return redirect('add_vendor')

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator

def vendor_list(request):

    # Get selected values
    selected_state = request.GET.get("state", "").strip()
    selected_city = request.GET.get("city", "").strip()
    selected_vendor = request.GET.get("vendor", "").strip()
    search = request.GET.get("search", "").strip()

    # Base Query
    vendors = Vendor.objects.all().order_by("-created_at")

    # ---------------------------
    # 1️⃣ STATE LIST
    # ---------------------------
    raw_states = Vendor.objects.exclude(state__isnull=True).exclude(state="") \
                    .values_list("state", flat=True).distinct()
    states = sorted({ s.strip().title() for s in raw_states })

    # ---------------------------
    # 2️⃣ CITY LIST (Depends on State)
    # ---------------------------
    if selected_state:
        raw_cities = Vendor.objects.filter(state__iexact=selected_state) \
                        .exclude(city__isnull=True).exclude(city="") \
                        .values_list("city", flat=True).distinct()
    else:
        raw_cities = Vendor.objects.exclude(city__isnull=True).exclude(city="") \
                        .values_list("city", flat=True).distinct()

    cities = sorted({ c.strip().title() for c in raw_cities })

    # ---------------------------
    # 3️⃣ Apply Filters
    # ---------------------------
    if selected_state:
        vendors = vendors.filter(state__iexact=selected_state)

    if selected_city:
        vendors = vendors.filter(city__iexact=selected_city)

    if selected_vendor:
        vendors = vendors.filter(id=selected_vendor)

    if search:
        vendors = vendors.filter(
            Q(vendor_id__icontains=search) |
            Q(vendor_name__icontains=search) |
            Q(company_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search)
        )

    # ---------------------------
    # 4️⃣ Vendor list (depends on State+City)
    # ---------------------------
    if selected_city:
        vendors_all = Vendor.objects.filter(city__iexact=selected_city).order_by("vendor_name")
    elif selected_state:
        vendors_all = Vendor.objects.filter(state__iexact=selected_state).order_by("vendor_name")
    else:
        vendors_all = Vendor.objects.all().order_by("vendor_name")

    # ---------------------------
    # Pagination
    # ---------------------------
    paginator = Paginator(vendors, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "vendor_list.html", {
        "vendors": page_obj,
        "states": states,
        "cities": cities,
        "vendors_all": vendors_all,

        "selected_state": selected_state,
        "selected_city": selected_city,
        "selected_vendor": selected_vendor,
        "search_query": search,

        "total_vendors": Vendor.objects.count(),
    })

def get_vendor_cities(request):
    state = request.GET.get("state", "")
    cities = Vendor.objects.filter(state__iexact=state).values_list("city", flat=True).distinct()
    return JsonResponse({"cities": sorted(list(cities))})

def get_vendors_by_city(request):
    city = request.GET.get("city", "")
    vendors = Vendor.objects.filter(city__iexact=city).values("id", "vendor_name", "company_name")
    return JsonResponse({"vendors": list(vendors)})

def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    employees = vendor.employees.all()
    vendor_products = vendor.products.all()

    return render(request, 'vendor_detail.html', {
        'vendor': vendor,
        'employees': employees,
        'vendor_products': vendor_products
    })

def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        try:
            vendor.company_name = request.POST.get('company_name', '').strip() or None
            vendor.vendor_name = request.POST.get('vendor_name', '').strip()
            vendor.phone_number = request.POST.get('phone_number', '').strip()
            vendor.phone_number_2 = request.POST.get('phone_number_2', '').strip() or None
            vendor.email = request.POST.get('email', '').strip() or None
            vendor.gstin = request.POST.get('gstin', '').strip() or None
            vendor.address_line_1 = request.POST.get('address_line_1', '').strip() or None
            vendor.address_line_2 = request.POST.get('address_line_2', '').strip() or None
            vendor.city = request.POST.get('city', '').strip() or None
            vendor.state = request.POST.get('state', '').strip() or None
            vendor.pincode = request.POST.get('pincode', '').strip() or None
            vendor.company_website = request.POST.get('company_website', '').strip() or None

            vendor.save()
            messages.success(request, f'Vendor "{vendor.vendor_name}" updated successfully!')
            return redirect('vendor_detail', vendor_id=vendor.id)

        except Exception as e:
            messages.error(request, f'Error updating vendor: {str(e)}')
            return redirect('edit_vendor', vendor_id=vendor_id)

    return render(request, 'edit_vendor.html', {'vendor': vendor})

def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        try:
            vendor_name = vendor.vendor_name
            vendor.delete()
            messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
            return redirect('vendor_list')
        except Exception as e:
            messages.error(request, f'Error deleting vendor: {str(e)}')
            return redirect('vendor_list')

    return render(request, 'delete_vendor.html', {'vendor': vendor})

def add_vendor_employee(request, vendor_id):
    """Add new employee linked to a vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        try:
            position = request.POST.get('position')
            name = request.POST.get('employee_name')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            date_of_birth = request.POST.get('date_of_birth')

            if not all([position, name, phone_number, email, date_of_birth]):
                messages.error(request, 'All fields are required!')
                return render(request, 'add_vendor_employee.html', {'vendor': vendor})

            VendorEmployee.objects.create(
                vendor=vendor,
                position=position,
                name=name,
                phone_number=phone_number,
                email=email,
                date_of_birth=date_of_birth
            )

            messages.success(request, f'Employee {name} added successfully!')
            return redirect('vendor_detail', vendor_id=vendor.id)

        except Exception as e:
            messages.error(request, f'Error adding employee: {str(e)}')
            return render(request, 'add_vendor_employee.html', {'vendor': vendor})

    return render(request, 'add_vendor_employee.html', {'vendor': vendor})

def edit_vendor_employee(request, employee_id):
    """Edit existing vendor employee"""
    employee = get_object_or_404(VendorEmployee, id=employee_id)
    vendor_id = employee.vendor.id

    if request.method == 'POST':
        try:
            employee.position = request.POST.get('position')
            employee.name = request.POST.get('employee_name')
            employee.phone_number = request.POST.get('phone_number')
            employee.email = request.POST.get('email')
            employee.date_of_birth = request.POST.get('date_of_birth')
            employee.save()

            messages.success(request, f'Employee {employee.name} updated successfully!')
            return redirect('vendor_detail', vendor_id=vendor_id)

        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')

    return render(request, 'edit_vendor_employee.html', {
        'employee': employee,
        'vendor': employee.vendor,
        'is_edit': True
    })

def delete_vendor_employee(request, employee_id):
    """Delete vendor employee"""
    employee = get_object_or_404(VendorEmployee, id=employee_id)
    vendor_id = employee.vendor.id

    if request.method == 'POST':
        try:
            employee_name = employee.name
            employee.delete()
            messages.success(request, f'Employee {employee_name} deleted successfully!')
            return redirect('vendor_detail', vendor_id=vendor_id)
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
            return redirect('vendor_detail', vendor_id=vendor_id)

    return render(request, 'delete_vendor_employee.html', {'employee': employee})

def add_vendor_product(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        try:
            product = VendorProduct.objects.create(
                vendor=vendor,
                product_id=request.POST.get('product_id'),
                product_name=request.POST.get('product_name'),
                selling_price=request.POST.get('selling_price'),
                purchase_price=request.POST.get('purchase_price') or None,
                tax_percent=request.POST.get('tax_percent') or None,
                product_unit=request.POST.get('product_unit'),
                warranty_period_date=request.POST.get('warranty_period_date') or None,
                installation_date=request.POST.get('installation_date') or None,
                hsn_sac=request.POST.get('hsn_sac'),
                category_id=request.POST.get('category_id') or None,
                description=request.POST.get('description'),
                manufacturer=request.POST.get('manufacturer'),
                serial_number=request.POST.get('serial_number'),
            )
            
            if request.FILES.get('product_image'):
                product.product_image = request.FILES['product_image']
                product.save()
            
            messages.success(request, f'Product "{product.product_name}" added successfully!')
            return redirect('vendor_detail', vendor_id=vendor.id)
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    context = {
        'vendor': vendor,
        'categories': categories,
    }
    return render(request, 'add_vendor_product.html', context)

def edit_vendor_product(request, product_id):
    product = get_object_or_404(VendorProduct, id=product_id)
    vendor = product.vendor
    categories = Category.objects.all()
    
    if request.method == 'POST':
        try:
            product.product_id = request.POST.get('product_id')
            product.product_name = request.POST.get('product_name')
            product.selling_price = request.POST.get('selling_price')
            product.installation_date = request.POST.get('installation_date') or None
            product.warranty_period_date = request.POST.get('warranty_period_date') or None
            product.purchase_price = request.POST.get('purchase_price') or None
            product.tax_percent = request.POST.get('tax_percent') or None
            product.product_unit = request.POST.get('product_unit')
            product.hsn_sac = request.POST.get('hsn_sac')
            product.category_id = request.POST.get('category_id') or None
            product.description = request.POST.get('description')
            product.manufacturer = request.POST.get('manufacturer')
            product.serial_number = request.POST.get('serial_number')
            
            if request.FILES.get('product_image'):
                product.product_image = request.FILES['product_image']
            
            product.save()
            messages.success(request, f'Product "{product.product_name}" updated successfully!')
            return redirect('vendor_detail', vendor_id=vendor.id)
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {
        'vendor': vendor,
        'product': product,
        'categories': categories,
    }
    return render(request, 'edit_vendor_product.html', context)

def delete_vendor_product(request, product_id):
    product = get_object_or_404(VendorProduct, id=product_id)
    vendor_id = product.vendor.id
    product_name = product.product_name
    
    if product.product_image:
        if os.path.isfile(product.product_image.path):
            os.remove(product.product_image.path)
    
    product.delete()
    messages.success(request, f'Product "{product_name}" deleted successfully!')
    return redirect('vendor_detail', vendor_id=vendor_id)

def generate_report(request):
    """Main reports dashboard view"""
    return render(request, 'generate_report.html')

def installation_report(request):
    """Installation reports view"""
    # Add your installation report logic here
    context = {
        'report_type': 'Installation',
        'title': 'Installation Reports'
    }
    return render(request, 'installation_report.html', context)

def service_report(request):
    """Service reports view"""
    # Add your service report logic here
    context = {
        'report_type': 'Service',
        'title': 'Service Reports'
    }
    return render(request, 'service_report.html', context)

def inspection_report(request):
    """Inspection reports view"""
    # Add your inspection report logic here
    context = {
        'report_type': 'Inspection',
        'title': 'Inspection Reports'
    }
    return render(request, 'inspection_report.html', context)

def incident_report(request):
    """Incident reports view"""
    # Add your incident report logic here
    context = {
        'report_type': 'Incident',
        'title': 'Incident Reports'
    }
    return render(request, 'incident_report.html', context)

def create_quotation(request):
    """Create a new quotation"""
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        formset = QuotationItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            quotation = form.save(commit=False)
            quotation.created_by = request.user
            quotation.save()
            
            # Save the formset
            formset.instance = quotation
            formset.save()
            
            # Calculate totals
            quotation.calculate_totals()
            
            messages.success(request, f'Quotation {quotation.quotation_number} created successfully!')
            return redirect('quotation_detail', quotation_id=quotation.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuotationForm()
        formset = QuotationItemFormSet()
        
        # Generate next quotation number
        last_quotation = Quotation.objects.filter(
            quotation_number__startswith='GK/NCP/2025/'
        ).order_by('-quotation_number').first()
        
        if last_quotation:
            try:
                last_num = int(last_quotation.quotation_number.split('/')[-1])
                next_num = f"GK/NCP/2025/{last_num + 1:03d}"
            except:
                next_num = "GK/NCP/2025/001"
        else:
            next_num = "GK/NCP/2025/001"
        
        form.initial['quotation_number'] = next_num
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Quotation'
    }
    return render(request, 'quotation_create.html', context)

def quotation_detail(request, quotation_id):
    """View quotation details"""
    quotation = get_object_or_404(Quotation, id=quotation_id)
    items = quotation.items.all()
    
    context = {
        'quotation': quotation,
        'items': items,
        'title': f'Quotation - {quotation.quotation_number}'
    }
    return render(request, 'quotation_detail.html', context)
 
def edit_quotation(request, quotation_id):
    """Edit existing quotation"""
    quotation = get_object_or_404(Quotation, id=quotation_id)
    
    if request.method == 'POST':
        form = QuotationForm(request.POST, instance=quotation)
        formset = QuotationItemFormSet(request.POST, instance=quotation)
        
        if form.is_valid() and formset.is_valid():
            quotation = form.save()
            formset.save()
            quotation.calculate_totals()
            
            messages.success(request, f'Quotation {quotation.quotation_number} updated successfully!')
            return redirect('quotation_detail', quotation_id=quotation.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuotationForm(instance=quotation)
        formset = QuotationItemFormSet(instance=quotation)
    
    context = {
        'form': form,
        'formset': formset,
        'quotation': quotation,
        'title': f'Edit Quotation - {quotation.quotation_number}'
    }
    return render(request, 'quotation_create.html', context)

def quotation_list(request):
    """List all quotations with search and filter"""
    search_form = QuotationSearchForm(request.GET)
    quotations = Quotation.objects.select_related('category', 'bank', 'tax_type', 'created_by').all()
    
    # Apply filters
    if search_form.is_valid():
        if search_form.cleaned_data.get('quotation_number'):
            quotations = quotations.filter(
                quotation_number__icontains=search_form.cleaned_data['quotation_number']
            )
        
        if search_form.cleaned_data.get('category'):
            quotations = quotations.filter(category=search_form.cleaned_data['category'])
        
        if search_form.cleaned_data.get('date_from'):
            quotations = quotations.filter(created_at__date__gte=search_form.cleaned_data['date_from'])
        
        if search_form.cleaned_data.get('date_to'):
            quotations = quotations.filter(created_at__date__lte=search_form.cleaned_data['date_to'])
        
        if search_form.cleaned_data.get('payment_terms'):
            quotations = quotations.filter(payment_terms=search_form.cleaned_data['payment_terms'])
    
    # Pagination
    paginator = Paginator(quotations, 10)  # 10 quotations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'title': 'Quotations List'
    }
    return render(request, 'quotation_list.html', context)

def quotation_report(request):
    """Quotation reports view"""
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    category_id = request.GET.get('category')
    
    # Base queryset
    quotations = Quotation.objects.select_related('category', 'created_by')
    
    # Apply filters
    if date_from:
        quotations = quotations.filter(created_at__date__gte=date_from)
    if date_to:
        quotations = quotations.filter(created_at__date__lte=date_to)
    if category_id:
        quotations = quotations.filter(category_id=category_id)
    
    # Calculate statistics
    total_quotations = quotations.count()
    total_value = quotations.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Recent quotations (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_quotations = quotations.filter(created_at__gte=thirty_days_ago).count()
    
    # Category-wise breakdown
    category_stats = quotations.values('category__name').annotate(
        count=models.Count('id'),
        total_value=Sum('total_amount')
    ).order_by('-total_value')
    
    # Monthly breakdown (last 12 months)
    monthly_stats = []
    for i in range(12):
        month_start = (datetime.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start.replace(month=month_start.month+1) if month_start.month < 12 
                    else month_start.replace(year=month_start.year+1, month=1)) - timedelta(days=1)
        
        month_quotations = quotations.filter(
            created_at__date__gte=month_start.date(),
            created_at__date__lte=month_end.date()
        )
        
        monthly_stats.append({
            'month': month_start.strftime('%B %Y'),
            'count': month_quotations.count(),
            'total_value': month_quotations.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        })
    
    monthly_stats.reverse()  # Show oldest first
    
    context = {
        'report_type': 'Quotation',
        'title': 'Quotation Reports',
        'total_quotations': total_quotations,
        'total_value': total_value,
        'recent_quotations': recent_quotations,
        'category_stats': category_stats,
        'monthly_stats': monthly_stats,
        'categories': Category.objects.all(),
        'date_from': date_from,
        'date_to': date_to,
        'selected_category': category_id
    }
    return render(request, 'quotation_report.html', context)

def delete_quotation(request, quotation_id):
    """Delete quotation"""
    quotation = get_object_or_404(Quotation, id=quotation_id)
    
    if request.method == 'POST':
        quotation_number = quotation.quotation_number
        quotation.delete()
        messages.success(request, f'Quotation {quotation_number} deleted successfully!')
        return redirect('quotation_list')
    
    context = {
        'quotation': quotation,
        'title': 'Delete Quotation'
    }
    return render(request, 'quotation_delete.html', context)

def ajax_calculate_totals(request):
    """AJAX endpoint to calculate totals"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            tax_percentage = Decimal(data.get('tax_percentage', 0))
            
            subtotal = Decimal('0.00')
            for item in items:
                quantity = Decimal(str(item.get('quantity', 0)))
                unit_price = Decimal(str(item.get('unit_price', 0)))
                subtotal += quantity * unit_price
            
            tax_amount = (subtotal * tax_percentage) / 100
            total = subtotal + tax_amount
            
            return JsonResponse({
                'success': True,
                'subtotal': str(subtotal),
                'tax_amount': str(tax_amount),
                'total': str(total)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def purchase_order_report(request):
    """Purchase order reports view"""
    # Add your purchase order report logic here
    context = {
        'report_type': 'Purchase Order',
        'title': 'Purchase Order Reports'
    }
    return render(request, 'purchase_order_report.html', context)

def delivery_challan_report(request):
    """Delivery challan reports view"""
    # Add your delivery challan report logic here
    context = {
        'report_type': 'Delivery Challan',
        'title': 'Delivery Challan Reports'
    }
    return render(request, 'delivery_challan_report.html', context)

def view_report(request):
    """Main reports dashboard view"""
    return render(request, 'view_reports.html')

from .models import *
from django.shortcuts import render, redirect
from .models import Staff

def add_staff(request):
    """Add new employee (general, not linked to customer/vendor)"""

    if request.method == 'POST':

        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')

        # Required fields validation
        if not name or not phone_number:
            return render(request, 'add_staff.html', {
                'error': "Name and Phone Number are required."
            })

        # Optional fields
        date_of_birth = request.POST.get('dob') or None
        email = request.POST.get('email') or None
        emergency_contact = request.POST.get('emergency_contact') or None
        pf_number = request.POST.get('pf_number') or None
        bank_name = request.POST.get('bank_name') or None
        bank_account_number = request.POST.get('bank_account_number') or None
        ifsc_code = request.POST.get('ifsc_code') or None
        pan_number = request.POST.get('pan_number') or None
        mother_name = request.POST.get('mother_name') or None
        father_name = request.POST.get('father_name') or None
        address = request.POST.get('address') or None
        aadhar_number = request.POST.get('aadhar_number') or None
        upload_photo = request.FILES.get('upload_photo') or None

        Staff.objects.create(
            name=name,
            date_of_birth=date_of_birth,
            email=email,
            phone_number=phone_number,
            emergency_contact=emergency_contact,
            pf_number=pf_number,
            bank_name=bank_name,
            bank_account_number=bank_account_number,
            ifsc_code=ifsc_code,
            pan_number=pan_number,
            mother_name=mother_name,
            father_name=father_name,
            address=address,
            aadhar_number=aadhar_number,
            upload_photo=upload_photo
        )

        return render(request, 'add_staff.html', {
            'success': f'Staff "{name}" successfully added!'
        })

    return render(request, 'add_staff.html')

def edit_staff(request, staff_id):
    """Edit existing staff record"""
    staff = get_object_or_404(Staff, id=staff_id)

    if request.method == "POST":
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        dob = request.POST.get("dob")

        if not name or not phone_number or not dob:
            messages.error(request, "Name, Phone Number and Date of Birth are required.")
            return render(request, "edit_staff.html", {"staff": staff})

        # Optional fields
        email = request.POST.get("email") or None
        emergency_contact = request.POST.get("emergency_contact") or None
        pf_number = request.POST.get("pf_number") or None
        bank_name = request.POST.get("bank_name") or None
        bank_account_number = request.POST.get("bank_account_number") or None
        ifsc_code = request.POST.get("ifsc_code") or None
        pan_number = request.POST.get("pan_number") or None
        mother_name = request.POST.get("mother_name") or None
        father_name = request.POST.get("father_name") or None
        address = request.POST.get("address") or None
        aadhar_number = request.POST.get("aadhar_number") or None
        upload_photo = request.FILES.get("upload_photo")

        # Update fields
        staff.name = name
        staff.phone_number = phone_number
        staff.date_of_birth = dob
        staff.email = email
        staff.emergency_contact = emergency_contact
        staff.pf_number = pf_number
        staff.bank_name = bank_name
        staff.bank_account_number = bank_account_number
        staff.ifsc_code = ifsc_code
        staff.pan_number = pan_number
        staff.mother_name = mother_name
        staff.father_name = father_name
        staff.address = address
        staff.aadhar_number = aadhar_number

        # Only replace photo if new one uploaded
        if upload_photo:
            staff.upload_photo = upload_photo

        staff.save()

        messages.success(request, f'Staff "{staff.name}" updated successfully.')
        return redirect("manage_staff")

    # GET – show edit form with existing data
    return render(request, "edit_staff.html", {"staff": staff})

from django.views.decorators.http import require_POST

def view_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    return render(request, "view_staff.html", {"staff": staff})

@require_POST
def delete_staff(request, staff_id):
    """Delete staff record"""
    staff = get_object_or_404(Staff, id=staff_id)
    name = staff.name
    staff.delete()
    messages.success(request, f'Staff "{name}" deleted successfully.')
    return redirect("manage_staff")

def assign_task1(request):
    """Assign task to employee"""

    if request.method == 'POST':
        assign_date = request.POST.get('assign_date')
        hospital_id = request.POST.get('hospital_id')
        staff_id = request.POST.get('staff_id')
        task_type = request.POST.get('task_type')
        description = request.POST.get('description')
        remarks = request.POST.get('remarks')
        follow_up_date = request.POST.get('follow_up_date')

        TaskAssign.objects.create(
            assign_date = assign_date,
            hospital_id = HospitalLead.objects.get(id=hospital_id),
            staff_id = Staff.objects.get(id=staff_id),
            task_type = task_type,
            description = description,
            remarks = remarks,
            follow_up_date = follow_up_date
        )
    
        hospitals = HospitalLead.objects.all()
        staff = Staff.objects.all()

        cities_list = HospitalLead.objects.values_list('city', flat=True) 
        cities = sorted(set([city.strip().title() for city in cities_list if city != '']))
        
        states_list = HospitalLead.objects.values_list('state', flat=True) 
        states = sorted(set([state.strip().title() for state in states_list if state != '']))

        return render(request, 'assign_task.html', {'success_message': f'Task assigned successfully!',
                                                    'staff': staff, 'hospitals': hospitals, 
                                                    'cities': cities, 'states':states})


    cities = set(HospitalLead.objects.values_list('city', flat=True))
    # This returns all unique cities as a set (the cities will not be repeated more than once)
    cities = [city.strip().title() for city in cities if city != '']
    '''Return a list of non-empty cities (if city != '') with surrounding whitespace removed (.strip()).
    title() - Capitalizes the first letter of every word.'''
    cities = sorted(set(cities))   # Sort the cities in ascending order
    
    states_list = HospitalLead.objects.values_list('state', flat=True) 
    states = sorted(set([state.strip().title() for state in states_list if state != '']))
      
    hospitals = HospitalLead.objects.all()
    staff = Staff.objects.all()

    return render(request, 'assign_task.html', {'staff': staff, 'hospitals': hospitals,
                                                'cities': cities, 'states': states})

def delete_task(request, task_id):
    task = get_object_or_404(TaskAssign, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully!")
    return redirect("manage_task")

from django.contrib import messages
from django.shortcuts import redirect

def assign_task(request):
    if request.method == 'POST':

        assign_date = request.POST.get('assign_date')
        hospital_id = request.POST.get('hospital_id')
        staff_id = request.POST.get('staff_id')
        task_type = request.POST.get('task_type')
        description = request.POST.get('description')
        remarks = request.POST.get('remarks')
        follow_up_date = request.POST.get('follow_up_date')

        TaskAssign.objects.create(
            assign_date=assign_date,
            hospital_id=HospitalLead.objects.get(id=hospital_id),
            staff_id=Staff.objects.get(id=staff_id),
            task_type=task_type,
            description=description,
            remarks=remarks,
            follow_up_date=follow_up_date
        )

        # success message (NOT shown on same page)
        messages.success(request, "Task assigned successfully!")

        # Return empty response for frontend JS
        return JsonResponse({"success": True})

    # Page load
    cities_list = HospitalLead.objects.values_list('city', flat=True)
    cities = sorted({c.strip().title() for c in cities_list if c})

    states_list = HospitalLead.objects.values_list('state', flat=True)
    states = sorted({s.strip().title() for s in states_list if s})

    return render(request, 'assign_task.html', {
        "staff": Staff.objects.all(),
        "hospitals": HospitalLead.objects.all(),
        "cities": cities,
        "states": states
    })

def manage_staff(request):
    selected_staff = request.GET.get("staff", "")

    if selected_staff:
        staff = Staff.objects.filter(id=selected_staff)
    else:
        staff = Staff.objects.all()

    return render(request, "manage_staff.html", {
        "staff": staff,
        "selected_staff": selected_staff,
        "staff_list": Staff.objects.all(),  # 🔥 for dropdown
    })

from django.shortcuts import render
from .models import TaskAssign, Staff, HospitalLead
import urllib.parse

def manage_task(request):

    # Base queryset
    tasks = TaskAssign.objects.all()

    # -------------------------------
    # FILTER PARAMETERS
    # -------------------------------
    selected_state = request.GET.get("state", "")
    selected_city = request.GET.get("city", "")
    selected_hospital = request.GET.get("hospital", "")
    selected_staff = request.GET.get("staff", "")
    selected_task_type = request.GET.get("task_type", "")

    # -------------------------------
    # FILTER BY STATE
    # -------------------------------
    if selected_state:
        tasks = tasks.filter(hospital_id__state__iexact=selected_state)

    # CITY LIST inside selected state
    if selected_state:
        cities = HospitalLead.objects.filter(state__iexact=selected_state)\
                .values_list("city", flat=True).distinct()
    else:
        cities = HospitalLead.objects.values_list("city", flat=True).distinct()

    # -------------------------------
    # FILTER BY CITY
    # -------------------------------
    if selected_city:
        tasks = tasks.filter(hospital_id__city__iexact=selected_city)

    # HOSPITAL LIST inside selected city
    if selected_city:
        hospitals = HospitalLead.objects.filter(city__iexact=selected_city)
    elif selected_state:
        hospitals = HospitalLead.objects.filter(state__iexact=selected_state)
    else:
        hospitals = HospitalLead.objects.all()

    # -------------------------------
    # FILTER BY HOSPITAL
    # -------------------------------
    if selected_hospital:
        tasks = tasks.filter(hospital_id=selected_hospital)

    # STAFF LIST inside selected hospital
    if selected_hospital:
        staff = Staff.objects.filter(task_assign__hospital_id=selected_hospital).distinct()
    else:
        staff = Staff.objects.all()

    # -------------------------------
    # FILTER BY STAFF
    # -------------------------------
    if selected_staff:
        tasks = tasks.filter(staff_id=selected_staff)

    # -------------------------------
    # FILTER BY TASK TYPE
    # -------------------------------
    if selected_task_type:
        tasks = tasks.filter(task_type=selected_task_type)

    # -------------------------------
    # STATE LIST
    # -------------------------------
    states = HospitalLead.objects.values_list("state", flat=True).distinct()

    return render(request, "manage-task.html", {
        "tasks": tasks,
        "states": states,
        "cities": cities,
        "hospitals": hospitals,
        "staff": staff,

        "selected_state": selected_state,
        "selected_city": selected_city,
        "selected_hospital": selected_hospital,
        "selected_staff": selected_staff,
        "selected_task_type": selected_task_type,
    })

def view_task(request, task_id):
    
    task = TaskAssign.objects.get(id = task_id)
    print(task.assign_date)
    return render(request, 'view-task.html', {'task' : task})

def edit_task(request, task_id):
    task = TaskAssign.objects.get(id=task_id)
    staff_list = Staff.objects.all()
    hospitals = HospitalLead.objects.all()

    if request.method == "POST":
        task.assign_date = request.POST.get("assign_date")
        task.follow_up_date = request.POST.get("follow_up_date")
        task.task_type = request.POST.get("task_type")
        task.description = request.POST.get("description")
        task.remarks = request.POST.get("remarks")
        task.staff_id_id = request.POST.get("staff_id")
        task.hospital_id_id = request.POST.get("hospital_id")

        task.save()
        return redirect("manage_task")

    return render(request, "edit-task.html", {
        "task": task,
        "staff_list": staff_list,
        "hospitals": hospitals,
    })

def Expenses(request):
    expenses = Expense.objects.all().order_by('-created_at')
    staff_list = Staff.objects.all()

    return render(request, "expenses.html", {
        'expenses': expenses,
        'staff_list': staff_list,
    })

def New_Expenses(request):
    if request.method == "POST":
        staff_id = request.POST.get("staff")
        expense_type = request.POST.get("expense_type")
        description = request.POST.get("description")
        bill_amount = request.POST.get("bill_amount")
        date = request.POST.get("date")
        remark = request.POST.get("remark")
        bill_file = request.FILES.get("bill_file")

        Expense.objects.create(
            staff_id=staff_id,
            expense_type=expense_type,
            description=description,
            bill_amount=bill_amount,
            date=date,
            remark=remark,
            bill_file=bill_file
        )

        messages.success(request, "Expense added successfully!")
        return redirect("Expenses")

    return redirect("Expenses")

from django.http import JsonResponse

def get_cities(request):
    state = request.GET.get("state")
    cities = HospitalLead.objects.filter(
        state=state, 
        lead_source="Customer"
    ).values_list("city", flat=True).distinct()
    return JsonResponse({"cities": list(cities)})

def get_hospitals(request):
    city = request.GET.get("city")
    hospitals = HospitalLead.objects.filter(
        city=city,
        lead_source="Customer"
    ).values("id", "hospital_name")
    return JsonResponse({"hospitals": list(hospitals)})

from django.http import JsonResponse
from .models import Vendor

def ajax_vendor_cities(request):
    state = request.GET.get("state", "")
    cities = list(Vendor.objects.filter(state__iexact=state)
                  .values_list("city", flat=True).distinct())
    return JsonResponse({"cities": cities})

def ajax_vendors_by_city(request):
    city = request.GET.get("city", "")
    vendors = Vendor.objects.filter(city__iexact=city).values(
        "id", "vendor_id", "vendor_name", "company_name"
    )
    return JsonResponse({"vendors": list(vendors)})


