def erro_usando_setas(text, pos_inicio, pos_fim):
	resultado = ''

	# Calculando idxs (indices)
	idx_inicio = max(text.rfind('\n', 0, pos_inicio.idx), 0)
	idx_fim = text.find('\n', idx_inicio + 1)
	if idx_fim < 0: idx_fim = len(text)
	

	line_count = pos_fim.ln - pos_inicio.ln + 1
	for i in range(line_count):
		# Calculate line columns
		line = text[idx_inicio:idx_fim]
		col_inicio = pos_inicio.col if i == 0 else 0
		col_fim = pos_fim.col if i == line_count - 1 else len(line) - 1

		# Resultado
		resultado += line + '\n'
		resultado += ' ' * col_inicio + '^' * (col_fim - col_inicio)

		# Re-calculate idxs
		idx_inicio = idx_fim
		idx_fim = text.find('\n', idx_inicio + 1)
		if idx_fim < 0: idx_fim = len(text)

	return resultado.replace('\t', '')
