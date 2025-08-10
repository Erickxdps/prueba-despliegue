# 🗂️ Scripts de Inicialización de Base de Datos

Esta carpeta contiene scripts para facilitar la gestión de la base de datos durante el desarrollo.

## 📋 Scripts Disponibles

### 1. `init_database.py` - Inicializar con Usuarios por Defecto
```bash
python init_database.py
```
- ✅ Crea tablas si no existen
- ✅ Crea usuarios por defecto si no existen
- ✅ Mantiene datos existentes

**Usuarios creados:**
- 👤 **Admin**: `admin` / `contra69882061`
- 👤 **Doctor**: `doctor` / `contra69882061`

### 2. `reset_database.py` - Recrear Base de Datos Completa
```bash
python reset_database.py
```
- ⚠️ **ELIMINA TODOS LOS DATOS**
- ✅ Recrea todas las tablas
- ✅ Crea usuarios por defecto
- 🔒 Requiere confirmación explícita

## 🚀 Uso Recomendado

### Primer uso o desarrollo:
```bash
python init_database.py
```

### Cuando quieras empezar de cero:
```bash
python reset_database.py
```

### Después de cambios en modelos:
```bash
python reset_database.py
```

## 🔐 Usuarios por Defecto

| Usuario | Contraseña | Rol | Permisos |
|---------|-----------|-----|----------|
| `admin` | `contra69882061` | admin | Todos los permisos |
| `doctor` | `contra69882061` | doctor | Permisos básicos |

## ⚠️ Seguridad

- 🚨 **CAMBIA LAS CONTRASEÑAS** en producción
- 🚨 Estos usuarios son **SOLO para desarrollo**
- 🚨 No uses estas credenciales en un entorno real

## 🛠️ Solución de Problemas

Si encuentras errores de importación, asegúrate de que:
1. Estás ejecutando desde la carpeta raíz del proyecto
2. La carpeta `app/` existe y contiene los archivos necesarios
3. Las dependencias están instaladas: `pip install -r requirements.txt`

---

💡 **Tip**: Después de recrear la base de datos, puedes cargar tu backup de datos si tienes uno.
