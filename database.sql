CREATE TABLE email.emails (
    email_id SERIAL PRIMARY KEY,
    sku VARCHAR(150) NOT NULL, -- sku
    email_receiver VARCHAR(255) NOT NULL, -- destinatario
    email_sender VARCHAR(255) NOT NULL, -- usuario que envia
    html_submit json NOT NULL -- html enviado
);