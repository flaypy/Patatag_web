"""
Script para inicializar o banco de dados
Execute este script antes de iniciar o servidor pela primeira vez
"""

from app import app, db
from models import User, Pet, Location, GeofenceZone, Alert

def init_database():
    """Criar todas as tabelas do banco de dados"""
    with app.app_context():
        print(">> Criando banco de dados...")

        # Deletar todas as tabelas (cuidado em producao!)
        db.drop_all()
        print("  [OK] Tabelas antigas removidas")

        # Criar todas as tabelas
        db.create_all()
        print("  [OK] Tabelas criadas com sucesso")

        # Verificar tabelas criadas
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        print(f"\nTabelas criadas ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")

        print("\n[SUCESSO] Banco de dados inicializado com sucesso!")
        print("\nProximos passos:")
        print("1. Execute: python app.py")
        print("2. Ou execute: python test_api.py")


def create_test_data():
    """Criar dados de teste"""
    with app.app_context():
        print("\n>> Criando dados de teste...")

        # Verificar se ja existe usuario de teste
        existing_user = User.query.filter_by(email='teste@teste.com').first()

        if existing_user:
            print("  [AVISO] Usuario de teste ja existe")
            return

        # Criar usuario de teste
        user = User(
            name='Usuario Teste',
            email='teste@teste.com'
        )
        user.set_password('123456')

        db.session.add(user)
        db.session.commit()

        print("  [OK] Usuario de teste criado")
        print(f"    Email: teste@teste.com")
        print(f"    Senha: 123456")

        print("\n[SUCESSO] Dados de teste criados com sucesso!")


if __name__ == '__main__':
    print("="*60)
    print("   PATATAG - Inicializacao do Banco de Dados")
    print("="*60)
    print()

    try:
        init_database()

        # Perguntar se quer criar dados de teste
        response = input("\nDeseja criar usuario de teste? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            create_test_data()

        print("\n" + "="*60)
        print("Pronto! Agora voce pode iniciar o servidor.")
        print("="*60)

    except Exception as e:
        print(f"\n[ERRO] Erro ao inicializar banco de dados: {e}")
        import traceback
        traceback.print_exc()
