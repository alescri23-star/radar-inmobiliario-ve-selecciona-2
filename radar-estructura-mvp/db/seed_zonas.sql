-- Zonas iniciales. Coordenadas = centroides APROXIMADOS (referencia visual, no límites).
-- Solo Barquisimeto está activa: activar otras zonas requiere aprobación.

INSERT INTO zonas (nombre, estado_ve, tipo, activa, centro) VALUES
    ('Barquisimeto',          'Lara',          'piloto', TRUE,  ST_GeogFromText('POINT(-69.3467 10.0678)')),
    ('Isla de Margarita',     'Nueva Esparta', 'tesis',  FALSE, ST_GeogFromText('POINT(-63.8697 10.9577)')),
    ('Los Roques',            'Dependencias Federales', 'tesis', FALSE, ST_GeogFromText('POINT(-66.6750 11.9500)')),
    ('Morrocoy',              'Falcón',        'tesis',  FALSE, ST_GeogFromText('POINT(-68.2667 10.8667)')),
    ('Tucacas',               'Falcón',        'tesis',  FALSE, ST_GeogFromText('POINT(-68.3245 10.7906)')),
    ('Chichiriviche',         'Falcón',        'tesis',  FALSE, ST_GeogFromText('POINT(-68.2730 10.9280)'))
ON CONFLICT (nombre) DO NOTHING;
