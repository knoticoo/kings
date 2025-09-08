-- Initialize event templates table and default templates
-- This script can be run when the application is available

-- Create event_templates table if it doesn't exist
CREATE TABLE IF NOT EXISTS event_templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    usage_count INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default templates
INSERT OR IGNORE INTO event_templates (name, description) VALUES
('Ежедневное событие', 'Стандартное ежедневное событие для всех игроков'),
('Турнир выходного дня', 'Специальный турнир, проводимый по выходным'),
('Специальное событие', 'Особое событие с уникальными правилами и наградами'),
('Событие альянса', 'Событие, в котором участвуют только члены альянсов'),
('Быстрое событие', 'Короткое событие с быстрыми результатами'),
('Сезонное событие', 'Событие, приуроченное к определенному сезону или празднику'),
('Событие новичков', 'Событие специально для новых игроков'),
('VIP событие', 'Эксклюзивное событие для опытных игроков');

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_event_templates_updated_at 
    AFTER UPDATE ON event_templates
    FOR EACH ROW
    BEGIN
        UPDATE event_templates SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;