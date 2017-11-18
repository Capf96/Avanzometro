from django.shortcuts import render
from apps.registro.models import Estudiante, Cursa
from django.core.cache import cache
import json

def obtenerMatriz(cohortes=None):
	jsonDict = []
	maxmatriz = 0
	if cohortes is None:
		porcentaje = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		creditos = ['0', '1-16', '17-32', '33-48', '49-64', '65-80', '81-96',
					'97-112', '113-128', '129-144', '145-160', '161-176', '177-192',
					'193-208', '209-224', '225-240', '240+']
		trimestres = ['Sept-Dic Año 1', 'Ene-Mar Año 1', 'Abr-Jul Año 1', 'Sept-Dic Año 2', 'Ene-Mar Año 2',
					  'Abr-Jul Año 2', 'Sept-Dic Año 3', 'Ene-Mar Año 3', 'Abr-Jul Año 3', 'Sept-Dic Año 4',
					  'Ene-Mar Año 4', 'Abr-Jul Año 4', 'Sept-Dic Año 5', 'Ene-Mar Año 5', 'Abr-Jul Año 5']

		matriz = []
		for _ in trimestres:
			matriz.append(porcentaje)

		jsonDict = []
		for j in range(len(matriz)):
			for i in range(17):
				dictdata = {'( % ) Porcentaje': matriz[j][i],
							'Créditos': creditos[i],
							'Trimestre': trimestres[j],
							'Vacío': 100,
							'Cohorte': 'XX'}

				jsonDict.append(dictdata)
		return jsonDict

	for cohorte in cohortes:
		matriz = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
		EstudianteDeCohorte = Estudiante.objects.filter(cohorte_id = cohorte)

		cuenta = EstudianteDeCohorte.count()
		trimestresVistos = []

		if int(cohorte) >= 68:
			anio = '19'
		else:
			anio = '20'

		cohorte_dada = cohorte

		trimestre = ['Sep-Dic ' + anio + str(int(cohorte_dada)),
					   'Ene-Mar ' + anio + str(int(cohorte_dada) + 1),
					   'Abr-Jul ' + anio + str(int(cohorte_dada) + 1),
					   'Sep-Dic ' + anio + str(int(cohorte_dada) + 1),
					   'Ene-Mar ' + anio + str(int(cohorte_dada) + 2),
					   'Abr-Jul ' + anio + str(int(cohorte_dada) + 2),
					   'Sep-Dic ' + anio + str(int(cohorte_dada) + 2),
					   'Ene-Mar ' + anio + str(int(cohorte_dada) + 3),
					   'Abr-Jul ' + anio + str(int(cohorte_dada) + 3),
					   'Sep-Dic ' + anio + str(int(cohorte_dada) + 3),
					   'Ene-Mar ' + anio + str(int(cohorte_dada) + 4),
					   'Abr-Jul ' + anio + str(int(cohorte_dada) + 4),
					   'Sep-Dic ' + anio + str(int(cohorte_dada) + 4),
					   'Ene-Mar ' + anio + str(int(cohorte_dada) + 5),
					   'Abr-Jul ' + anio + str(int(cohorte_dada) + 5)]

		categoriaCreditos = ['0', '1-16', '17-32', '33-48', '49-64', '65-80', '81-96',
					'97-112', '113-128', '129-144', '145-160', '161-176', '177-192',
					'193-208', '209-224', '225-240', '240+']

		for estudianteAct in EstudianteDeCohorte:
			# Filtramos los cursa de un estudiante
			cursaEstudiante = Cursa.objects.filter(estudiante = estudianteAct)
			for cursaAct in cursaEstudiante:
				# identificamos el trimestre de ese cursa
				trimestreVar = cursaAct.trimestre.id
				if trimestreVar in trimestresVistos:
					pass
				else:
					trimestresVistos.append(trimestreVar)
					temp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					matriz.append(temp)

		for estudianteAct in EstudianteDeCohorte:
			# Filtramos los cursa de un estudiante
			cursaEstudiante = Cursa.objects.filter(estudiante = estudianteAct)
			for cursaAct in cursaEstudiante:
				# identificamos el trimestre de ese cursa
				trimestreVar = cursaAct.trimestre.id
				if trimestreVar in trimestresVistos:
					posicion = trimestre.index(trimestreVar) + 1 # +1 por el trim 0
					creditos = cursaAct.creditosAprobados
					if creditos <= 240:
						if creditos != 0:
							matriz[posicion][int((creditos - 1)/ 16) + 1] += 1
						else:
							matriz[posicion][0] += 1
					else:
						matriz[posicion][16] += 1

				else:
					trimestresVistos.append(trimestreVar)
					temp = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
					matriz.append(temp)

		for i in range(len(matriz)):
			for j in range(len(matriz[i])):
				matriz[i][j] = matriz[i][j] * 100 / cuenta

		matriz = matriz[1:]

		for j in range(len(matriz)):
			t = 'Año: ' + str(j//3 + 1) + ' Trimestre: ' + str(j%3 + 1)
			for i in range(17):
				dictdata = {'( % ) Porcentaje': matriz[j][i],
							'Créditos': categoriaCreditos[i],
							'Trimestre': t,
							'Vacío': "",
							'Cohorte': cohorte}

				jsonDict.append(dictdata)

	return jsonDict


def multigrafica(request):
	cache.clear()
	list1 = []
	for i in range(68, 118):
		a = str(i)[-2] + str(i)[-1]
		list1.append(a)

	# PARA PROBAR AQUI PONEN CUALES TRIMESTRES QUIEREN VER!!!
	jsondata = obtenerMatriz(['87', '88'])

	jsondata = json.dumps(jsondata)

	return render(request, "multigraph.html",{'data2': jsondata, 'mls': 1000, })
