CREATE TABLE logs.emails (
    email_id SERIAL PRIMARY KEY,
    sku VARCHAR(150) NOT NULL, -- sku
    email_receiver VARCHAR(255) NOT NULL, -- destinatario
    email_sender VARCHAR(255) NOT NULL, -- usuario que envia
    html_submit json NOT NULL, -- html enviado
	message_send VARCHAR(500) NOT NULL
	created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
);
