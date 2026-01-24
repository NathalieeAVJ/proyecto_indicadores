import os
import django
import random
import uuid
from faker import Faker
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User, AuditLog
from inventory.models import PhoneNumber, RadioBase, SparePartCategory, SparePart
from incidencias.models import FailureType, Incident, RadioBaseIncident
from rrhh.models import Employee, Payroll, FamilyMember, Equipment, Absence

fake = Faker('es_ES')

def seed_data():
    print("Iniciando Siembra de Datos Maestro NatTelf (Versión Nathaliee Vargas)...")

    # Limpieza inicial para asegurar jerarquía limpia
    print("Limpiando datos previos para coherencia de jerarquía...")
    # Payroll.objects.all().delete()
    # Absence.objects.all().delete()
    # Equipment.objects.all().delete()
    # RadioBaseIncident.objects.all().delete()
    # Employee.objects.all().delete()
    # User.objects.filter(is_superuser=False).delete()

    # 1. LA PRESIDENCIA (Nivel 0)
    print("Estableciendo la Presidencia...")
    pres_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'n.vargas@nattelf.com', 
            'first_name': 'Nathaliee', 
            'last_name': 'Vargas', 
            'role': 'admin'
        }
    )
    pres_user.set_password('admin123')
    pres_user.save()

    nathaliee, _ = Employee.objects.get_or_create(
        dni='V-00000001',
        defaults={
            'first_name': 'Nathaliee',
            'last_name': 'Vargas',
            'email': 'n.vargas@nattelf.com',
            'phone': '0212-7000001',
            'position': 'Presidenta de NatTelf',
            'department': 'Presidencia',
            'rank': 0,
            'hire_date': '2010-01-01',
            'base_salary': Decimal('25000.00'),
            'system_user': pres_user
        }
    )

    # 2. VICE PRESIDENCIA (Nivel 1)
    print("Creando Vice Presidencias...")
    
    # VP Operaciones
    vp_ops_user, _ = User.objects.get_or_create(
        username='vp_operaciones',
        defaults={'email': 'vp.ops@nattelf.com', 'first_name': 'Elena', 'last_name': 'Guerra', 'role': 'admin'}
    )
    vp_ops_user.set_password('admin123')
    vp_ops_user.save()

    vp_ops, _ = Employee.objects.get_or_create(
        dni='V-11111111',
        defaults={
            'first_name': 'Elena',
            'last_name': 'Guerra',
            'email': 'e.guerra@nattelf.com',
            'phone': '0212-1111111',
            'position': 'Vice Presidente de Operaciones',
            'department': 'Operaciones',
            'rank': 1,
            'supervisor': nathaliee,
            'hire_date': '2012-05-15',
            'base_salary': Decimal('12000.00'),
            'system_user': vp_ops_user
        }
    )

    # VP RRHH
    vp_rrhh_user, _ = User.objects.get_or_create(
        username='vp_rrhh',
        defaults={'email': 'vp.rrhh@nattelf.com', 'first_name': 'Marcos', 'last_name': 'Pérez', 'role': 'admin'}
    )
    vp_rrhh_user.set_password('admin123')
    vp_rrhh_user.save()

    vp_rrhh, _ = Employee.objects.get_or_create(
        dni='V-12121212',
        defaults={
            'first_name': 'Marcos',
            'last_name': 'Pérez',
            'email': 'm.perez@nattelf.com',
            'phone': '0212-1212121',
            'position': 'Vice Presidente de Capital Humano',
            'department': 'Recursos Humanos',
            'rank': 1,
            'supervisor': nathaliee,
            'hire_date': '2013-02-10',
            'base_salary': Decimal('11500.00'),
            'system_user': vp_rrhh_user
        }
    )

    # 3. GERENCIAS (Nivel 3)
    print("Creando Gerencias de Área...")
    
    # Gerente Operaciones Caracas
    gte_ops_user, _ = User.objects.get_or_create(
        username='gerente_ops',
        defaults={'email': 'gte.ops@nattelf.com', 'first_name': 'Ricardo', 'last_name': 'Silva', 'role': 'evaluator'}
    )
    gte_ops_user.set_password('admin123')
    gte_ops_user.save()

    gte_ops, _ = Employee.objects.get_or_create(
        dni='V-22222222',
        defaults={
            'first_name': 'Ricardo',
            'last_name': 'Silva',
            'email': 'r.silva@nattelf.com',
            'phone': '0412-2222222',
            'position': 'Gerente de Infraestructura',
            'department': 'Operaciones',
            'rank': 3,
            'supervisor': vp_ops,
            'hire_date': '2015-08-20',
            'base_salary': Decimal('4500.00'),
            'system_user': gte_ops_user
        }
    )

    # 4. PERSONAL OPERATIVO (Nivel 5)
    print("Creando personal operativo y técnicos...")
    caracas_zones = ["Altamira", "Las Mercedes", "Chacao", "Catia", "Petare"]
    
    for i in range(10):
        tec_user, _ = User.objects.get_or_create(
            username=f'tecnico_{i+1}',
            defaults={
                'email': f'tec{i+1}@nattelf.com', 
                'first_name': fake.first_name(), 
                'last_name': fake.last_name(), 
                'role': 'technician'
            }
        )
        tec_user.set_password('password123')
        tec_user.save()

        tec, _ = Employee.objects.get_or_create(
            dni=f'V-3000000{i}',
            defaults={
                'first_name': tec_user.first_name,
                'last_name': tec_user.last_name,
                'email': tec_user.email,
                'phone': fake.phone_number()[:20],
                'address': f"Caracas, {random.choice(caracas_zones)}",
                'position': 'Técnico de Redes',
                'department': 'Operaciones',
                'rank': 5,
                'supervisor': gte_ops,
                'hire_date': fake.date_between(start_date='-2y', end_date='-1y'),
                'base_salary': Decimal(str(random.randint(1200, 1800))),
                'system_user': tec_user
            }
        )

    # 5. DATA OPERATIVA (Radiobases e Incidencias)
    print("Poblando Radiobases e Incidencias...")
    tipos = ["Corte de Fibra", "Falla de Energía", "Vandalismo", "Mantenimiento Preventivo"]
    all_types = [FailureType.objects.get_or_create(name=t)[0] for t in tipos]

    for i in range(15):
        rb, _ = RadioBase.objects.get_or_create(
            code=f"RB-CCS-{100 + i}",
            defaults={
                'name': f"Base {random.choice(caracas_zones)} {i+1}",
                'location': "Caracas",
                'latitude': random.uniform(10.45, 10.51),
                'longitude': random.uniform(-66.95, -66.80)
            }
        )
        
        for _ in range(random.randint(0, 2)):
            RadioBaseIncident.objects.create(
                title=f"Falla en {rb.name}",
                description="Incidencia crítica detectada por hardware.",
                radio_base=rb,
                failure_type=random.choice(all_types),
                start_date=timezone.now() - timedelta(days=random.randint(1, 10)),
                created_by=pres_user,
                status=random.choice(['pending', 'in_review', 'solved'])
            )

    # 6. HISTORIAL DE NÓMINA (3 Meses)
    print("Generando historial de nómina para validación de recibos...")
    for emp in Employee.objects.all():
        for mes in [11, 12, 1]:
            Payroll.objects.get_or_create(
                employee=emp,
                period_month=mes,
                period_year=2025 if mes > 10 else 2026,
                defaults={
                    'base_salary': emp.base_salary,
                    'food_stamps': Decimal('40.00'),
                    'bonuses': Decimal(str(random.randint(50, 200))),
                    'deductions': Decimal(str(random.randint(20, 100))),
                    'payment_status': 'paid',
                    'payment_date': (timezone.now() - timedelta(days=random.randint(1, 30))).date()
                }
            )

    # 7. INVENTARIO DE REPUESTOS PARA RADIOBASES
    print("Creando inventario de repuestos para radiobases...")
    
    # Categorías de repuestos
    categorias_data = [
        {"name": "Cables y Conectores", "description": "Cables de fibra óptica, coaxiales, conectores RF y accesorios de conexión"},
        {"name": "Antenas", "description": "Antenas sectoriales, omnidireccionales, parabólicas y accesorios"},
        {"name": "Equipos de Energía", "description": "Baterías, rectificadores, UPS, paneles solares y reguladores"},
        {"name": "Equipos de Transmisión", "description": "Radios, amplificadores, combinadores y duplexores"},
        {"name": "Protección y Seguridad", "description": "Pararrayos, supresores de picos, fusibles y protectores"},
        {"name": "Torres y Estructuras", "description": "Herrajes, abrazaderas, soportes y materiales estructurales"},
        {"name": "Herramientas", "description": "Herramientas especializadas para mantenimiento de radiobases"},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        cat, _ = SparePartCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"description": cat_data["description"]}
        )
        categorias[cat_data["name"]] = cat
    
    # Repuestos
    repuestos_data = [
        # Cables y Conectores
        {"code": "CAB-FO-SM-50", "name": "Cable Fibra Óptica Monomodo 50m", "category": "Cables y Conectores", "unit_price": 85.00, "quantity": 25, "min_stock": 5, "location": "A1-01"},
        {"code": "CAB-FO-SM-100", "name": "Cable Fibra Óptica Monomodo 100m", "category": "Cables y Conectores", "unit_price": 150.00, "quantity": 15, "min_stock": 3, "location": "A1-02"},
        {"code": "CAB-COAX-LMR400", "name": "Cable Coaxial LMR-400 (por metro)", "category": "Cables y Conectores", "unit_price": 4.50, "quantity": 500, "min_stock": 100, "location": "A1-03"},
        {"code": "CON-N-MALE", "name": "Conector N Macho para LMR-400", "category": "Cables y Conectores", "unit_price": 8.50, "quantity": 100, "min_stock": 20, "location": "A1-04"},
        {"code": "CON-N-FEMALE", "name": "Conector N Hembra para LMR-400", "category": "Cables y Conectores", "unit_price": 9.00, "quantity": 80, "min_stock": 20, "location": "A1-05"},
        {"code": "CON-SMA-MALE", "name": "Conector SMA Macho", "category": "Cables y Conectores", "unit_price": 5.00, "quantity": 150, "min_stock": 30, "location": "A1-06"},
        {"code": "PATCH-FO-SC", "name": "Patch Cord Fibra SC/SC 3m", "category": "Cables y Conectores", "unit_price": 12.00, "quantity": 50, "min_stock": 10, "location": "A1-07"},
        
        # Antenas
        {"code": "ANT-SECT-120", "name": "Antena Sectorial 120° 17dBi", "category": "Antenas", "unit_price": 450.00, "quantity": 8, "min_stock": 2, "location": "B1-01"},
        {"code": "ANT-OMNI-10", "name": "Antena Omnidireccional 10dBi", "category": "Antenas", "unit_price": 180.00, "quantity": 12, "min_stock": 3, "location": "B1-02"},
        {"code": "ANT-PARAB-30", "name": "Antena Parabólica 30dBi", "category": "Antenas", "unit_price": 320.00, "quantity": 6, "min_stock": 2, "location": "B1-03"},
        {"code": "ANT-YAGI-15", "name": "Antena Yagi 15dBi", "category": "Antenas", "unit_price": 95.00, "quantity": 10, "min_stock": 3, "location": "B1-04"},
        {"code": "SOPT-ANT-U", "name": "Soporte Universal para Antena", "category": "Antenas", "unit_price": 35.00, "quantity": 30, "min_stock": 10, "location": "B1-05"},
        
        # Equipos de Energía
        {"code": "BAT-12V-100AH", "name": "Batería AGM 12V 100Ah", "category": "Equipos de Energía", "unit_price": 280.00, "quantity": 20, "min_stock": 4, "location": "C1-01"},
        {"code": "BAT-12V-200AH", "name": "Batería AGM 12V 200Ah", "category": "Equipos de Energía", "unit_price": 450.00, "quantity": 12, "min_stock": 2, "location": "C1-02"},
        {"code": "RECT-48V-30A", "name": "Rectificador 48V 30A", "category": "Equipos de Energía", "unit_price": 850.00, "quantity": 5, "min_stock": 1, "location": "C1-03"},
        {"code": "UPS-3KVA", "name": "UPS Online 3KVA", "category": "Equipos de Energía", "unit_price": 1200.00, "quantity": 4, "min_stock": 1, "location": "C1-04"},
        {"code": "PANEL-SOLAR-100W", "name": "Panel Solar 100W Monocristalino", "category": "Equipos de Energía", "unit_price": 120.00, "quantity": 15, "min_stock": 3, "location": "C1-05"},
        {"code": "REG-SOLAR-30A", "name": "Regulador Solar MPPT 30A", "category": "Equipos de Energía", "unit_price": 85.00, "quantity": 10, "min_stock": 2, "location": "C1-06"},
        
        # Equipos de Transmisión
        {"code": "RADIO-UHF-25W", "name": "Radio UHF 25W Digital", "category": "Equipos de Transmisión", "unit_price": 650.00, "quantity": 8, "min_stock": 2, "location": "D1-01"},
        {"code": "AMP-RF-50W", "name": "Amplificador RF 50W", "category": "Equipos de Transmisión", "unit_price": 380.00, "quantity": 6, "min_stock": 2, "location": "D1-02"},
        {"code": "DUPLEXOR-UHF", "name": "Duplexor UHF 50W", "category": "Equipos de Transmisión", "unit_price": 290.00, "quantity": 8, "min_stock": 2, "location": "D1-03"},
        {"code": "COMB-4-PORT", "name": "Combinador 4 Puertos", "category": "Equipos de Transmisión", "unit_price": 520.00, "quantity": 4, "min_stock": 1, "location": "D1-04"},
        
        # Protección y Seguridad
        {"code": "PARARRAYOS-RF", "name": "Pararrayos Coaxial RF", "category": "Protección y Seguridad", "unit_price": 65.00, "quantity": 30, "min_stock": 10, "location": "E1-01"},
        {"code": "SUPRESOR-AC", "name": "Supresor de Picos AC", "category": "Protección y Seguridad", "unit_price": 45.00, "quantity": 25, "min_stock": 5, "location": "E1-02"},
        {"code": "FUSIBLE-30A", "name": "Fusible Cilíndrico 30A", "category": "Protección y Seguridad", "unit_price": 3.50, "quantity": 100, "min_stock": 20, "location": "E1-03"},
        {"code": "PROTECT-ETH", "name": "Protector PoE Ethernet", "category": "Protección y Seguridad", "unit_price": 28.00, "quantity": 40, "min_stock": 10, "location": "E1-04"},
        {"code": "TIERRA-KIT", "name": "Kit de Puesta a Tierra", "category": "Protección y Seguridad", "unit_price": 75.00, "quantity": 15, "min_stock": 3, "location": "E1-05"},
        
        # Torres y Estructuras
        {"code": "HERRAJE-U-4", "name": "Herraje en U 4 pulgadas", "category": "Torres y Estructuras", "unit_price": 12.00, "quantity": 80, "min_stock": 20, "location": "F1-01"},
        {"code": "ABRAZADERA-50MM", "name": "Abrazadera Galvanizada 50mm", "category": "Torres y Estructuras", "unit_price": 8.00, "quantity": 100, "min_stock": 25, "location": "F1-02"},
        {"code": "MASTIL-3M", "name": "Mástil Galvanizado 3m", "category": "Torres y Estructuras", "unit_price": 95.00, "quantity": 10, "min_stock": 2, "location": "F1-03"},
        {"code": "TENSOR-CABLE", "name": "Tensor para Cable de Acero", "category": "Torres y Estructuras", "unit_price": 15.00, "quantity": 50, "min_stock": 10, "location": "F1-04"},
        
        # Herramientas
        {"code": "TOOL-CRIMP-RJ", "name": "Crimpadora RJ45/RJ11", "category": "Herramientas", "unit_price": 25.00, "quantity": 10, "min_stock": 2, "location": "G1-01"},
        {"code": "TOOL-CRIMP-COAX", "name": "Crimpadora Conectores Coaxiales", "category": "Herramientas", "unit_price": 85.00, "quantity": 5, "min_stock": 1, "location": "G1-02"},
        {"code": "TOOL-FIBER-KIT", "name": "Kit Empalme Fibra Óptica", "category": "Herramientas", "unit_price": 450.00, "quantity": 3, "min_stock": 1, "location": "G1-03"},
        {"code": "TOOL-ANALIZADOR", "name": "Analizador de Espectro Portátil", "category": "Herramientas", "unit_price": 1800.00, "quantity": 2, "min_stock": 1, "location": "G1-04"},
    ]
    
    for rep_data in repuestos_data:
        SparePart.objects.get_or_create(
            code=rep_data["code"],
            defaults={
                "name": rep_data["name"],
                "category": categorias.get(rep_data["category"]),
                "description": f"Repuesto para mantenimiento de radiobases - {rep_data['name']}",
                "unit_price": Decimal(str(rep_data["unit_price"])),
                "quantity_in_stock": rep_data["quantity"],
                "minimum_stock": rep_data["min_stock"],
                "location": rep_data["location"]
            }
        )
    
    print(f"  ✓ {len(categorias_data)} categorías de repuestos creadas")
    print(f"  ✓ {len(repuestos_data)} repuestos agregados al inventario")

    print("\n--- SIEMBRA FINALIZADA ---")
    print(f"LA PRESIDENTA: admin / admin123 (Nombre: Nathaliee Vargas)")
    print(f"VP OPERACIONES: vp_operaciones / admin123")
    print(f"GERENTE DE ÁREA: gerente_ops / admin123")
    print(f"PLANTA TÉCNICA: tecnico_1...10 / password123")
    print(f"\nINVENTARIO: {len(repuestos_data)} repuestos en {len(categorias_data)} categorías")

if __name__ == "__main__":
    seed_data()
