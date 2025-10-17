from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models.expense import ExpenseModel
from models.budget import BudgetModel  # ← NUEVO: Importar BudgetModel
from utils.helpers import decimal_to_float
from datetime import datetime
import traceback

class ExpenseController:
    def __init__(self):
        self.bp = Blueprint('expenses', '__name__', url_prefix='/expenses')
        self.expense_model = ExpenseModel()
        self.budget_model = BudgetModel()  # ← NUEVO: Instanciar BudgetModel
        self.register_routes()

    def register_routes(self):
        self.bp.route('/')(self.index)
        self.bp.route('/add', methods=['POST'])(self.add)
        self.bp.route('/delete/<int:expense_id>', methods=['POST'])(self.delete)
        self.bp.route('/api')(self.api_expenses)
        # ✅ NUEVA RUTA AGREGADA
        self.bp.route('/editar_gasto', methods=['POST'])(self.editar_gasto)

    def index(self):
        """Página de listado de gastos"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user_id = session['user_id']
        
        # Obtener mes seleccionado (por defecto mes actual)
        mes_seleccionado = request.args.get('mes', datetime.now().strftime('%Y-%m'))
        
        try:
            año, mes = mes_seleccionado.split('-')
            año = int(año)
            mes = int(mes)
        except (ValueError, AttributeError):
            # Si hay error en el formato, usar mes actual
            ahora = datetime.now()
            mes_seleccionado = ahora.strftime('%Y-%m')
            año = ahora.year
            mes = ahora.month
        
        # Obtener datos del mes seleccionado
        expenses = self.expense_model.get_by_user(user_id, mes, año)
        categories = self.expense_model.get_categories()
        total_mes = self.expense_model.get_total(user_id, mes, año)
        
        # Obtener total general de todos los gastos (sin filtro de mes)
        total_general = self.expense_model.get_total(user_id)
        total_registros = len(expenses)
        
        # ✅ CALCULAR SALDO ACTUAL (INGRESOS TOTALES - GASTOS TOTALES) - NUEVO
        try:
            # Obtener total de ingresos
            ingresos_query = "SELECT COALESCE(SUM(monto), 0) as total_ingresos FROM ingresos WHERE usuario_id = %s"
            ingresos_result = self.expense_model.db.execute_query(ingresos_query, (user_id,), fetch_one=True)
            total_ingresos = float(ingresos_result['total_ingresos']) if ingresos_result and ingresos_result['total_ingresos'] else 0
            
            # Obtener total de gastos (usando el mismo método que en dashboard)
            gastos_query = "SELECT COALESCE(SUM(monto), 0) as total_gastos FROM gastos WHERE usuario_id = %s"
            gastos_result = self.expense_model.db.execute_query(gastos_query, (user_id,), fetch_one=True)
            total_gastos = float(gastos_result['total_gastos']) if gastos_result and gastos_result['total_gastos'] else 0
            
            # Calcular saldo actual
            saldo_actual = total_ingresos - total_gastos
            
            # Debug: imprimir valores para verificar
            print(f"DEBUG - User ID: {user_id}")
            print(f"DEBUG - Total Ingresos: {total_ingresos}")
            print(f"DEBUG - Total Gastos: {total_gastos}")
            print(f"DEBUG - Saldo Actual: {saldo_actual}")
            print(f"DEBUG - Total General (método anterior): {total_general}")
            
        except Exception as e:
            print(f"Error calculando saldo actual: {e}")
            saldo_actual = 0
    
        return render_template('transactions/expenses.html',
                             expenses=expenses,
                             categories=categories,
                             total_mes=total_mes,
                             total_general=total_general,
                             total_registros=total_registros,
                             saldo_actual=saldo_actual,  # ← NUEVO
                             mes_seleccionado=mes_seleccionado,
                             now=datetime.now())

    def add(self):
        """Agregar nuevo gasto"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            print("=== 🚨 DEBUG INICIANDO - FORMULARIO GASTO ===")
            
            # Debug: imprimir TODOS los datos del formulario
            print("📋 TODOS LOS DATOS DEL FORMULARIO:")
            for key, value in request.form.items():
                print(f"   {key}: {value}")
            
            concepto = request.form.get('concepto')
            monto = request.form.get('monto')
            categoria_id = request.form.get('categoria_id')
            fecha = request.form.get('fecha')
            
            # Debug del campo esencial
            esencial_checkbox = request.form.get('esencial')
            print(f"🔍 DEBUG ESENCIAL - Valor crudo: '{esencial_checkbox}'")
            print(f"🔍 DEBUG ESENCIAL - Tipo: {type(esencial_checkbox)}")
            
            # Procesar el valor
            if esencial_checkbox == 'on':
                esencial = True
                print("🔍 DEBUG ESENCIAL - Checkbox: SELECCIONADO")
            else:
                esencial = False
                print("🔍 DEBUG ESENCIAL - Checkbox: NO SELECCIONADO")
            
            descripcion = request.form.get('descripcion')
            
            print(f"🎯 VALORES FINALES:")
            print(f"   concepto: {concepto}")
            print(f"   monto: {monto}")
            print(f"   categoria_id: {categoria_id}")
            print(f"   fecha: {fecha}")
            print(f"   esencial: {esencial}")
            print(f"   descripcion: {descripcion}")
            
            if not all([concepto, monto, categoria_id, fecha]):
                flash('Por favor completa todos los campos obligatorios', 'error')
                return redirect(url_for('expenses.index'))
            
            try:
                user_id = session['user_id']
                
                # Limpiar formato y convertir a float
                monto_limpio = monto.replace('.', '')
                monto_float = float(monto_limpio)
                
                print(f"💰 MONTO PROCESADO: {monto_float}")
                
                if monto_float <= 0:
                    flash('El monto debe ser mayor a 0', 'error')
                    return redirect(url_for('expenses.index'))
                
                # ✅ VALIDACIÓN 2: Verificar que el gasto no supere el saldo disponible
                # Obtener saldo actual (ingresos totales - gastos totales)
                ingresos_query = "SELECT COALESCE(SUM(monto), 0) as total_ingresos FROM ingresos WHERE usuario_id = %s"
                ingresos_result = self.expense_model.db.execute_query(ingresos_query, (user_id,), fetch_one=True)
                total_ingresos = float(ingresos_result['total_ingresos']) if ingresos_result and ingresos_result['total_ingresos'] else 0
                
                gastos_query = "SELECT COALESCE(SUM(monto), 0) as total_gastos FROM gastos WHERE usuario_id = %s"
                gastos_result = self.expense_model.db.execute_query(gastos_query, (user_id,), fetch_one=True)
                total_gastos = float(gastos_result['total_gastos']) if gastos_result and gastos_result['total_gastos'] else 0
                
                saldo_actual = total_ingresos - total_gastos
                
                # Verificar si el nuevo gasto supera el saldo disponible
                if monto_float > saldo_actual:
                    flash(f'No puedes gastar más de tu saldo disponible. Saldo actual: ${saldo_actual:,.0f}', 'error')
                    return redirect(url_for('expenses.index'))
                
                # ✅ VALIDACIÓN 3: NUEVA - Verificar que el gasto no supere el presupuesto de la categoría
                # Obtener el presupuesto de la categoría seleccionada
                budget = self.budget_model.get_budget_by_category(user_id, int(categoria_id))
                
                if budget:
                    presupuesto_maximo = float(budget['monto_maximo'])
                    gasto_actual = float(budget['gasto_actual'])
                    saldo_presupuesto = presupuesto_maximo - gasto_actual
                    
                    # Verificar si el nuevo gasto supera el presupuesto disponible
                    if monto_float > saldo_presupuesto:
                        categoria_nombre = self._get_category_name(int(categoria_id))
                        flash(f'No puedes gastar más del presupuesto asignado para {categoria_nombre}. '
                              f'Presupuesto disponible: ${saldo_presupuesto:,.0f}', 'error')
                        return redirect(url_for('expenses.index'))
                
                print("✅ PASÓ VALIDACIONES - CREANDO GASTO...")
                print(f"📝 DATOS PARA CREAR:")
                print(f"   user_id: {user_id}")
                print(f"   concepto: {concepto}")
                print(f"   monto: {monto_float}")
                print(f"   categoria_id: {categoria_id}")
                print(f"   fecha: {fecha}")
                print(f"   esencial: {esencial}")
                print(f"   descripcion: {descripcion}")
                
                # Crear el gasto
                expense_id = self.expense_model.create(
                    user_id, concepto, monto_float, 
                    int(categoria_id), fecha, esencial, descripcion
                )
                
                print(f"🎉 GASTO CREADO CON ID: {expense_id}")
                
                # ✅ DEBUG EXTRA: Verificar el gasto recién creado
                if expense_id:
                    gasto_creado = self.expense_model.db.execute_query(
                        "SELECT * FROM gastos WHERE id = %s", 
                        (expense_id,), 
                        fetch_one=True
                    )
                    print(f"🔍 VERIFICANDO GASTO EN BD:")
                    print(f"   ID: {gasto_creado['id']}")
                    print(f"   Concepto: {gasto_creado['concepto']}")
                    print(f"   Esencial en BD: {gasto_creado['esencial']}")
                    print(f"   Tipo de esencial: {type(gasto_creado['esencial'])}")
                
                flash('¡Gasto agregado exitosamente!', 'success')
                
            except ValueError:
                flash('El monto ingresado no es válido', 'error')
                return redirect(url_for('expenses.index'))
            except Exception as e:
                print(f"💥 ERROR: {str(e)}")
                traceback.print_exc()
                flash('Error al agregar gasto: ' + str(e), 'error')
            
            print("=== 🚨 DEBUG FINALIZADO - FORMULARIO GASTO ===")
        
        return redirect(url_for('expenses.index'))

    def editar_gasto(self):
        """✅ NUEVO MÉTODO: Editar gasto existente"""
        print("=== 🚨 DEBUG: INICIANDO EDICIÓN DE GASTO ===")
        print(f"🌐 DEBUG: Ruta accedida: {request.url}")
        print(f"🌐 DEBUG: Método: {request.method}")
        
        if 'user_id' not in session:
            print("❌ DEBUG: Usuario no autenticado")
            return redirect(url_for('auth.login'))
        
        if request.method == 'POST':
            try:
                # Debug: imprimir todos los datos del formulario
                print("📋 DEBUG: Datos del formulario recibidos:")
                for key, value in request.form.items():
                    print(f"   {key}: {value}")
                
                gasto_id = request.form.get('id')
                concepto = request.form.get('concepto')
                monto = request.form.get('monto')
                categoria_id = request.form.get('categoria_id')
                fecha = request.form.get('fecha')
                # ✅ CORREGIDO: Usar el mismo método que en add()
                esencial = request.form.get('esencial') == 'on'
                descripcion = request.form.get('descripcion', '')
                user_id = session['user_id']

                print(f"🔍 DEBUG: user_id={user_id}, gasto_id={gasto_id}")
                print(f"🔍 DEBUG: esencial={esencial}")

                # Verificar que el gasto pertenece al usuario
                expense = self.expense_model.db.execute_query(
                    "SELECT * FROM gastos WHERE id = %s AND usuario_id = %s",
                    (gasto_id, user_id),
                    fetch_one=True
                )
                
                if not expense:
                    print("❌ DEBUG: Gasto no encontrado o no pertenece al usuario")
                    flash('No tienes permiso para editar este gasto', 'error')
                    return redirect(url_for('expenses.index'))

                print("✅ DEBUG: Gasto validado, procediendo a actualizar...")

                # Convertir monto a float
                monto_float = float(monto)
                
                # Actualizar en la base de datos
                update_query = """
                    UPDATE gastos 
                    SET concepto = %s, monto = %s, categoria_id = %s, fecha = %s, 
                        esencial = %s, descripcion = %s
                    WHERE id = %s AND usuario_id = %s
                """
                self.expense_model.db.execute_query(
                    update_query, 
                    (concepto, monto_float, categoria_id, fecha, esencial, descripcion, gasto_id, user_id)
                )
                
                print("🎉 DEBUG: Gasto actualizado exitosamente")
                flash('¡Gasto actualizado exitosamente!', 'success')
                
            except Exception as e:
                print(f"💥 DEBUG: Error al editar gasto: {str(e)}")
                print(f"💥 DEBUG: Tipo de error: {type(e).__name__}")
                print(f"💥 DEBUG: Traceback completo:")
                traceback.print_exc()
                flash('Error al editar el gasto: ' + str(e), 'error')
        
        print("=== 🚨 DEBUG: FINALIZANDO EDICIÓN DE GASTO ===")
        return redirect(url_for('expenses.index'))

    def _get_category_name(self, categoria_id):
        """Método auxiliar para obtener el nombre de una categoría"""
        try:
            query = "SELECT nombre FROM categorias_gastos WHERE id = %s"
            result = self.expense_model.db.execute_query(query, (categoria_id,), fetch_one=True)
            return result['nombre'] if result else 'Categoría'
        except:
            return 'Categoría'

    def delete(self, expense_id):
        """Eliminar gasto"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autorizado'}), 401
        
        try:
            # Verificar que el gasto pertenezca al usuario
            expense = self.expense_model.db.execute_query(
                "SELECT * FROM gastos WHERE id = %s AND usuario_id = %s",
                (expense_id, session['user_id']),
                fetch_one=True
            )
            
            if not expense:
                return jsonify({'success': False, 'error': 'Gasto no encontrado'}), 404
            
            delete_query = "DELETE FROM gastos WHERE id = %s"
            self.expense_model.db.execute_query(delete_query, (expense_id,))
            flash('Gasto eliminado exitosamente', 'success')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_expenses(self):
        """API para obtener gastos (AJAX)"""
        if 'user_id' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        
        user_id = session['user_id']
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        expenses = self.expense_model.get_by_user(user_id, month, year)
        
        # Convertir decimales a float
        for expense in expenses:
            expense['monto'] = decimal_to_float(expense['monto'])
            if expense['fecha']:
                expense['fecha'] = expense['fecha'].strftime('%Y-%m-%d')
        
        return jsonify(expenses)

# Crear instancia del controlador
expense_controller = ExpenseController()