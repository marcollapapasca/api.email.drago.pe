#!/bin/bash

PORT=3006
SCRIPT="python /drago/api.email.drago.pe/src/main.py"
LOG_FILE="my_log_file.log"

# Listar procesos en ejecución en el puerto especificado
echo "Procesos en ejecución en el puerto $PORT:"
ss -tuln | grep ":$PORT"

# Obtener PIDs de los procesos en el puerto utilizando fuser
pids=$(fuser $PORT/tcp 2>/dev/null)

# Filtrar PIDs que corresponden al script específico
filtered_pids=()
for pid in $pids; do
  cmdline=$(ps -p $pid -o cmd=)
  if [[ "$cmdline" == *"$SCRIPT"* ]]; then
    filtered_pids+=($pid)
  fi
done

# Verificar si se encontraron procesos
if [ ${#filtered_pids[@]} -eq 0 ]; then
  echo "No se encontraron procesos en ejecución en el puerto $PORT ejecutando $SCRIPT."
else
  echo "Eliminando procesos en ejecución en el puerto $PORT ejecutando $SCRIPT: ${filtered_pids[@]}"
  # Matar procesos
  for pid in "${filtered_pids[@]}"; do
    kill -9 $pid
    echo "Proceso $pid eliminado."
  done

  # Esperar un momento para asegurarse de que los procesos sean eliminados
  sleep 2

  # Verificar si el puerto sigue ocupado
  pids_check=$(fuser $PORT/tcp 2>/dev/null)
  if [ -z "$pids_check" ]; then
    echo "El puerto $PORT está libre."
  else
    echo "No se pudo liberar el puerto $PORT. Procesos restantes: $pids_check"
    exit 1
  fi
fi

# Iniciar el proceso nuevamente con nohup
nohup $SCRIPT > $LOG_FILE 2>&1 &
echo "Proceso iniciado con nohup y redirigido a $LOG_FILE."
