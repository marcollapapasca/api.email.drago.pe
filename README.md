# api.email.drago.pe
uvicorn app:app --host 0.0.0.0 --port 3006 --reload
uvicorn app:app --host 0.0.0.0 --port 3006 

** USERS
[GET] /api/users



[1] Después de que se alcanza el límite de tarifa del destinatario, los mensajes no se pueden enviar desde el buzón hasta que el número de destinatarios que se enviaron mensajes en las últimas 24 horas cae por debajo del límite. Por ejemplo, un usuario envía un mensaje de correo electrónico a 5000 destinatarios a las 09:00 AM, luego envía otro mensaje a 2500 destinatarios a las 10:00 AM, y luego envía otro mensaje a 2500 destinatarios a las 11:00 AM, llegando al límite de 10.000 mensajes. El usuario no podrá volver a enviar mensajes hasta las 09:00 AM al día siguiente.


[X] posibles problemas de bloqueo
- Cuando son varios correos que no son validos y retornan mensaje de error
