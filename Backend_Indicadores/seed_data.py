import os
import django
import random
from faker import Faker
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User
from inventory.models import PhoneNumber, RadioBase, SparePartCategory, SparePart
from incidencias.models import FailureType, Incident, RadioBaseIncident, WorkOrder
from rrhh.models import Employee, Payroll, Department, Equipment
from documentos.models import Folder, BusinessDocument, DocumentVersion
from procura.models import Supplier, SupplierContact, Contract, PurchaseOrder, SupplierEvaluation
from ventas.models import SimCard, Customer, Sale

fake = Faker('es_ES')

def seed_data():
    print("🚀 Iniciando Super-Siembra NatTelf (50+ registros por entidad)...")

    # 0. LIMPIEZA TOTAL
    print("🧹 Limpiando base de datos completa (excepto Nathaliee)...")
    
    # 0.1 Dependientes de Segundo Nivel (Hojas extremas)
    WorkOrder.objects.all().delete()
    Payroll.objects.all().delete()
    SupplierEvaluation.objects.all().delete()
    Sale.objects.all().delete()
    
    # 0.2 Dependientes de Primer Nivel
    Incident.objects.all().delete()
    RadioBaseIncident.objects.all().delete()
    PurchaseOrder.objects.all().delete()
    Contract.objects.all().delete()
    SimCard.objects.all().delete()
    BusinessDocument.objects.all().delete()
    Equipment.objects.all().delete()
    
    # 0.3 Entidades Base
    Department.objects.all().delete()
    Employee.objects.exclude(dni='V-00000001').delete()
    User.objects.filter(role__in=['technician', 'evaluator']).delete() # Limpiar roles creados por seeder
    User.objects.exclude(username__in=['admin', 'nathaliee']).delete() # Mantener solo admin principal
    
    PhoneNumber.objects.all().delete()
    RadioBase.objects.all().delete()
    SparePart.objects.all().delete()
    SparePartCategory.objects.all().delete()
    FailureType.objects.all().delete()
    Folder.objects.all().delete()
    Supplier.objects.all().delete()
    Customer.objects.all().delete()

    # 1. DEPARTAMENTOS (Jerarquía)
    print("🏢 Estableciendo jerarquía de Departamentos...")
    dep_presidencia = Department.objects.create(name="Presidencia", description="Dirección general y toma de decisiones estratégicas.")
    
    dep_operaciones = Department.objects.create(name="Operaciones", description="Gestión de red, radiobases y mantenimiento de campo.", parent=dep_presidencia)
    dep_soporte = Department.objects.create(name="Soporte Técnico", description="Atención remota y coordinación de incidencias.", parent=dep_operaciones)
    dep_campo = Department.objects.create(name="Ingeniería de Campo", description="Despliegue y reparación física de infraestructura.", parent=dep_operaciones)
    
    dep_rrhh = Department.objects.create(name="Recursos Humanos", description="Gestión de capital humano, nómina y bienestar.", parent=dep_presidencia)
    dep_finanzas = Department.objects.create(name="Finanzas", description="Gestión presupuestaria y contabilidad corporativa.", parent=dep_presidencia)
    dep_auditoria = Department.objects.create(name="Auditoría de Servicio", description="Control de calidad, auditoría de tiempos y evaluación de desempeño.", parent=dep_presidencia)

    # 1B. USUARIOS Y EMPLEADOS BASE
    print("👥 Creando estructura jerárquica inicial...")
    
    pres_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'n.vargas@nattelf.com', 'first_name': 'Nathaliee', 'last_name': 'Vargas', 'role': 'admin'}
    )
    pres_user.set_password('admin123')
    pres_user.save()

    nathaliee, created = Employee.objects.get_or_create(
        dni='V-00000001',
        defaults={
            'first_name': 'Nathaliee', 'last_name': 'Vargas', 'email': 'n.vargas@nattelf.com',
            'position': 'Presidenta', 'department': 'Presidencia', 'department_ref': dep_presidencia,
            'rank': 0, 'hire_date': '2010-01-01',
            'base_salary': Decimal('25000.00'), 'system_user': pres_user
        }
    )
    if not created:
        nathaliee.department_ref = dep_presidencia
        nathaliee.save()

    # 1C. ESTRUCTURA DE PERSONAL POR DEPARTAMENTO
    print("👥 Generando estructura jerárquica por departamentos (Gerentes + Empleados)...")
    
    # Definición de departamentos y sus cargos
    dept_structure = {
        dep_operaciones: {"manager_pos": "Gerente de Operaciones", "staff_pos": "Ingeniero de Redes", "staff_count": 8},
        dep_soporte: {"manager_pos": "Gerente de Soporte", "staff_pos": "Analista de Soporte", "staff_count": 6},
        dep_campo: {"manager_pos": "Gerente de Campo", "staff_pos": "Técnico de Campo", "staff_count": 12},
        dep_rrhh: {"manager_pos": "Gerente de RRHH", "staff_pos": "Especialista de RRHH", "staff_count": 4},
        dep_finanzas: {"manager_pos": "Gerente de Finanzas", "staff_pos": "Contador", "staff_count": 4},
        dep_auditoria: {"manager_pos": "Gerente de Auditoría", "staff_pos": "Auditor Interno", "staff_count": 3},
    }

    all_techs = [] # Para asignar a incidencias después
    
    for dept, info in dept_structure.items():
        # 1. Crear Gerente del Departamento
        m_username = f"gerente_{dept.name.lower().replace(' ', '_')}"
        m_user, _ = User.objects.get_or_create(
            username=m_username,
            defaults={
                'email': f"{m_username}@nattelf.com",
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'role': 'admin' if dept in [dep_rrhh, dep_finanzas] else 'evaluator'
            }
        )
        m_user.set_password('password123')
        m_user.save()

        manager = Employee.objects.create(
            dni=fake.unique.bothify(text='V-########'),
            first_name=m_user.first_name,
            last_name=m_user.last_name,
            email=m_user.email,
            position=info["manager_pos"],
            department=dept.name,
            department_ref=dept,
            rank=3, # Gerente
            supervisor=nathaliee,
            system_user=m_user,
            base_salary=Decimal(random.randint(3500, 5000)),
            hire_date=fake.date_between(start_date='-5y', end_date='-2y')
        )

        # 2. Crear Empleados subordinados
        for i in range(info["staff_count"]):
            s_username = f"emp_{dept.name.lower().replace(' ', '_')}_{i+1}"
            s_user = User.objects.create(
                username=s_username,
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role='technician' if dept in [dep_operaciones, dep_soporte, dep_campo] else 'user'
            )
            s_user.set_password('password123')
            s_user.save()

            employee = Employee.objects.create(
                dni=fake.unique.bothify(text='V-########'),
                first_name=s_user.first_name,
                last_name=s_user.last_name,
                email=s_user.email,
                position=info["staff_pos"],
                department=dept.name,
                department_ref=dept,
                rank=5, # Operativo
                supervisor=manager,
                system_user=s_user,
                base_salary=Decimal(random.randint(1200, 2200)),
                hire_date=fake.date_between(start_date='-2y', end_date='-1m')
            )
            
            if s_user.role == 'technician':
                all_techs.append(s_user)

    # Nota: Los evaluadores de auditoría específicos ahora se manejan en el loop anterior
    evaluadores = list(User.objects.filter(role='evaluator'))
    techs = all_techs # Sobrescribir referencia para el resto del seeder (incidencias)

    # 3. TELÉFONOS E INCIDENCIAS NACIONALES (50 registros cada uno)
    print("📞 Generando 50 Números y 50 Incidencias Telefónicas...")
    tipos_falla = ["Corte de Fibra", "Falla de Energía", "Vandalismo", "Mantenimiento Preventivo", "Error de Configuración"]
    failure_objs = [FailureType.objects.create(name=t) for t in tipos_falla]
    
    for i in range(1, 51):
        phone = PhoneNumber.objects.create(
            number=fake.unique.bothify(text='0311-#######'),
            description=f'Línea Corporativa {i}', department=random.choice(['Ventas', 'Soporte', 'RRHH', 'Admin'])
        )
        
        created_at = timezone.now() - timedelta(days=random.randint(5, 30))
        status = random.choice(['pending', 'in_review', 'solved'])
        assigned_at = created_at + timedelta(hours=random.randint(1, 10))
        solved_date = assigned_at + timedelta(hours=random.randint(2, 48))

        inc = Incident.objects.create(
            title=f"Falla en Línea {phone.number}", description=fake.sentence(),
            phone_number=phone, failure_type=random.choice(failure_objs),
            start_date=created_at, created_by=pres_user, assigned_to=random.choice(techs),
            status=status, assigned_at=assigned_at if status != 'pending' else None,
            solved_date=solved_date if status == 'solved' else None
        )
        inc.created_at = created_at
        inc.save()

    # 4. RADIOBASES Y TICKETS RB (50 registros cada uno)
    print("📡 Generando 50 Radiobases y 50 Tickets de Infraestructura...")
    for i in range(1, 51):
        code = fake.unique.bothify(text='RB-CCS-###')
        rb = RadioBase.objects.create(
            code=code, name=f"Estación {fake.city()} ({code})", location=fake.address(),
            latitude=random.uniform(10.4, 10.6), longitude=random.uniform(-67.0, -66.8)
        )
        
        created_at = timezone.now() - timedelta(days=random.randint(1, 45))
        status = random.choice(['pending', 'in_review', 'solved'])
        assigned_at = created_at + timedelta(hours=random.randint(1, 10))
        solved_date = assigned_at + timedelta(hours=random.randint(2, 48))

        rb_inc = RadioBaseIncident.objects.create(
            title=f"Avería en {rb.code}", description=fake.text(max_nb_chars=50),
            radio_base=rb, failure_type=random.choice(failure_objs),
            start_date=created_at, created_by=pres_user, assigned_to=random.choice(techs),
            status=status, assigned_at=assigned_at if status != 'pending' else None,
            solved_date=solved_date if status == 'solved' else None
        )
        rb_inc.created_at = created_at
        rb_inc.save()

    # 5. INVENTARIO DE REPUESTOS (50 registros)
    print("📦 Generando 50 ítems de Repuestos...")
    cat_inv, _ = SparePartCategory.objects.get_or_create(name="Electrónica General")
    for i in range(1, 51):
        SparePart.objects.create(
            code=f"REP-{i:04}",
            name=f"Repuesto T-100{i} {fake.word().upper()}",
            category=cat_inv,
            unit_price=Decimal(str(random.randint(5, 500))),
            quantity_in_stock=random.randint(10, 100),
            minimum_stock=10,
            location=f"Pasillo {random.randint(1,10)}-B"
        )

    # 5B. EQUIPOS E INVENTARIO (50 registros)
    print("💻 Generando 50 Activos de Inventario (Asignados y en Stock)...")
    brands = {
        'laptop': ['Dell', 'HP', 'Lenovo', 'Apple'],
        'phone': ['Samsung', 'iPhone', 'Xiaomi'],
        'tool': ['Stanley', 'Bosh', 'Makita'],
        'furniture': ['Herman Miller', 'Ikea'],
        'id_card': ['NatTelf Oficial'],
        'uniform': ['Dotación NatTelf']
    }
    all_employees = list(Employee.objects.all())
    for i in range(1, 51):
        cat = random.choice(['laptop', 'phone', 'tool', 'furniture', 'id_card', 'uniform'])
        brand_list = brands.get(cat, ['Genérico'])
        brand = random.choice(brand_list)
        emp = random.choice(all_employees) if random.random() > 0.4 else None
        
        Equipment.objects.create(
            internal_code=f"NT-{cat[0].upper()}-{i:04}",
            item_name=f"{brand} {cat.capitalize()}",
            brand=brand,
            model=f"Mod-{random.randint(100, 999)}",
            category=cat,
            serial_number=fake.bothify(text='??-####-####').upper(),
            status=random.choice(['functional', 'functional', 'functional', 'failing']),
            employee=emp
        )

    # 6. HISTORIAL DE NÓMINA (50 registros del último mes)
    print("💰 Generando 50 Recibos de Nómina...")
    for emp in Employee.objects.all()[:50]:
        Payroll.objects.get_or_create(
            employee=emp, period_month=1, period_year=2026,
            defaults={
                'base_salary': emp.base_salary, 'food_stamps': Decimal('40.00'),
                'bonuses': Decimal(str(random.randint(100, 500))),
                'deductions': Decimal(str(random.randint(50, 150))),
                'payment_status': 'pending'
            }
        )

    # 7. GESTIÓN DOCUMENTAL (Carpetas y Documentos)
    print("📁 Generando estructura de Gestión Documental...")
    
    # Carpetas principales
    folder_contratos = Folder.objects.create(name="Contratos", description="Contratos legales y comerciales", icon="mdi-file-document", created_by=pres_user)
    folder_facturas = Folder.objects.create(name="Facturas", description="Facturas y comprobantes", icon="mdi-receipt", created_by=pres_user)
    folder_tecnicos = Folder.objects.create(name="Documentos Técnicos", description="Manuales y planos", icon="mdi-file-cog", created_by=pres_user)
    folder_rrhh = Folder.objects.create(name="RRHH", description="Documentos de recursos humanos", icon="mdi-account-group", created_by=pres_user)
    
    # Subcarpetas
    folder_contratos_2024 = Folder.objects.create(name="2024", parent=folder_contratos, description="Contratos del año 2024", created_by=pres_user)
    folder_contratos_2025 = Folder.objects.create(name="2025", parent=folder_contratos, description="Contratos del año 2025", created_by=pres_user)
    
    # Documentos de ejemplo
    categorias_doc = ['contract', 'invoice', 'blueprint', 'certificate', 'report', 'manual']
    carpetas = [folder_contratos, folder_facturas, folder_tecnicos, folder_rrhh, folder_contratos_2024, folder_contratos_2025]
    
    print("📄 Generando 30 documentos de ejemplo...")
    for i in range(1, 31):
        cat = random.choice(categorias_doc)
        folder = random.choice(carpetas)
        
        doc = BusinessDocument.objects.create(
            title=f"{cat.capitalize()} NatTelf {i:03d}",
            category=cat,
            folder=folder,
            description=fake.text(max_nb_chars=100),
            tags=f"{cat}, nattelf, {random.choice(['importante', 'urgente', 'revision'])}",
            uploaded_by=random.choice([pres_user] + techs[:5]),
            version_number=1
        )
        
        # Crear versión inicial
        DocumentVersion.objects.create(
            document=doc,
            version_number=1,
            uploaded_by=doc.uploaded_by,
            notes="Versión inicial"
        )
        
        # Algunos documentos con múltiples versiones
        if random.random() > 0.7:
            doc.version_number = 2
            doc.save()
            DocumentVersion.objects.create(
                document=doc,
                version_number=2,
                uploaded_by=random.choice(techs[:3]),
                notes="Actualización de contenido"
            )

    # 8. PORTAL DE PROVEEDORES Y CONTRATISTAS
    print("🏢 Generando proveedores y contratistas...")
    
    categorias_prov = ['materials', 'services', 'construction', 'maintenance', 'consulting', 'transport']
    proveedores = []
    
    for i in range(1, 21):
        supplier = Supplier.objects.create(
            name=f"{fake.company()} C.A.",
            rif=f"J-{random.randint(10000000, 99999999)}-{random.randint(0, 9)}",
            email=fake.company_email(),
            phone=fake.bothify(text='0212-#######'),
            address=fake.address(),
            website=f"www.{fake.domain_name()}",
            category=random.choice(categorias_prov),
            status=random.choice(['active', 'active', 'active', 'inactive']),
            created_by=pres_user
        )
        proveedores.append(supplier)
        
        # Contacto principal para cada proveedor
        SupplierContact.objects.create(
            supplier=supplier,
            name=fake.name(),
            position=random.choice(['Gerente Ventas', 'Director Comercial', 'Ejecutivo de Cuentas']),
            email=fake.email(),
            phone=fake.bothify(text='0414-#######'),
            is_primary=True
        )
        
        # Algunos proveedores con contacto secundario
        if random.random() > 0.6:
            SupplierContact.objects.create(
                supplier=supplier,
                name=fake.name(),
                position=random.choice(['Asistente', 'Coordinador', 'Supervisor']),
                email=fake.email(),
                phone=fake.bothify(text='0424-#######'),
                is_primary=False
            )

    # Contratos
    print("📋 Generando contratos con proveedores...")
    for i in range(1, 16):
        supplier = random.choice(proveedores)
        start_date = fake.date_between(start_date='-1y', end_date='today')
        end_date = fake.date_between(start_date='today', end_date='+1y')
        
        Contract.objects.create(
            supplier=supplier,
            contract_number=f"CNT-{2024+random.randint(0,1)}-{i:04d}",
            title=f"Contrato de {supplier.get_category_display()}",
            description=fake.text(max_nb_chars=200),
            start_date=start_date,
            end_date=end_date,
            value=Decimal(str(random.randint(50000, 500000))),
            status=random.choice(['active', 'active', 'draft', 'expired']),
            created_by=pres_user
        )

    # Órdenes de Compra
    print("🛒 Generando órdenes de compra...")
    contratos = list(Contract.objects.all())
    for i in range(1, 31):
        supplier = random.choice(proveedores)
        contract = random.choice(contratos) if random.random() > 0.3 else None
        
        PurchaseOrder.objects.create(
            supplier=supplier,
            order_number=f"OC-{2025}-{i:05d}",
            contract=contract,
            description=f"Orden de compra para {fake.catch_phrase()}",
            total_amount=Decimal(str(random.randint(5000, 100000))),
            status=random.choice(['pending', 'approved', 'received', 'approved']),
            requested_by=random.choice([pres_user] + techs[:5]),
            requested_date=fake.date_between(start_date='-60d', end_date='today'),
            delivery_date=fake.date_between(start_date='today', end_date='+30d')
        )

    # Evaluaciones de Proveedores
    print("⭐ Generando evaluaciones de proveedores...")
    for supplier in proveedores[:12]:
        for _ in range(random.randint(1, 3)):
            quality_score = random.randint(3, 5)
            delivery_score = random.randint(3, 5)
            service_score = random.randint(3, 5)
            price_score = random.randint(3, 5)
            compliance_score = random.randint(3, 5)
            
            SupplierEvaluation.objects.create(
                supplier=supplier,
                evaluator=random.choice([pres_user] + evaluadores),
                evaluation_date=fake.date_between(start_date='-6m', end_date='today'),
                quality_score=quality_score,
                delivery_score=delivery_score,
                service_score=service_score,
                price_score=price_score,
                compliance_score=compliance_score,
                comments=fake.text(max_nb_chars=150)
            )

    # 9. VENTAS DE SIM CARDS Y ESIM
    print("📱 Generando Inventario de SIM Cards y eSIM...")
    all_phones = list(PhoneNumber.objects.all())
    
    # Crear stock de SIMs (algunas con número asignado, otras no)
    for i in range(1, 41):
        is_esim = random.random() > 0.6
        status = 'available'
        phone = None
        
        # El 40% de las SIMs disponibles ya tienen un número pre-asignado del pool
        if random.random() > 0.6 and all_phones:
            phone = all_phones.pop(0)
            
        SimCard.objects.create(
            iccid=f"89580400{random.randint(1000000000, 9999999999)}",
            type='esim' if is_esim else 'physical',
            status=status,
            phone_number=phone,
            puk=fake.bothify(text='########'),
            pin=fake.bothify(text='####')
        )

    print("👥 Generando base de datos de Clientes...")
    clientes = []
    for _ in range(1, 16):
        c = Customer.objects.create(
            name=fake.name(),
            dni=fake.unique.bothify(text='??-########').upper(),
            email=fake.email(),
            phone=fake.bothify(text='04##-#######'),
            address=fake.address()
        )
        clientes.append(c)

    print("💰 Generando histórico de ventas...")
    sims_to_sell = SimCard.objects.all()[:10]
    admins = list(User.objects.filter(role__in=['admin', 'evaluator']))
    for sim in sims_to_sell:
        cust = random.choice(clientes)
        Sale.objects.create(
            customer=cust,
            sim_card=sim,
            amount=Decimal(str(random.randint(10, 50))),
            payment_method=random.choice(['cash', 'card', 'transfer', 'zelle']),
            seller=random.choice(admins),
            notes="Venta procesada en punto de venta físico"
        )

    print("\n✅ ¡SUPER-SIEMBRA COMPLETADA EXITOSAMENTE!")
    print("----------------------------------------")
    print(f"Total Usuarios/Empleados: {Employee.objects.count()}")
    print(f"Total Incidencias (Tel): {Incident.objects.count()}")
    print(f"Total Incidencias (RB):  {RadioBaseIncident.objects.count()}")
    print(f"Total Repuestos:         {SparePart.objects.count()}")
    print(f"Total Equipos Activos:   {Equipment.objects.count()}")
    print(f"Total Carpetas:          {Folder.objects.count()}")
    print(f"Total Documentos:        {BusinessDocument.objects.count()}")
    print(f"Total Proveedores:       {Supplier.objects.count()}")
    print(f"Total Contratos:         {Contract.objects.count()}")
    print(f"Total Órdenes Compra:    {PurchaseOrder.objects.count()}")
    print(f"Total Evaluaciones:      {SupplierEvaluation.objects.count()}")
    print(f"Total SIMs en Stock:     {SimCard.objects.count()}")
    print(f"Total Clientes (Cédula): {Customer.objects.count()}")
    print(f"Total Ventas Realizadas: {Sale.objects.count()}")
    print("----------------------------------------")

if __name__ == "__main__":
    seed_data()
