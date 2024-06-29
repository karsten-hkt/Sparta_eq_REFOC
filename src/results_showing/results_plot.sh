gmt begin ../../output/results_showing/sparta png
	# Place modern session commands here 36.48296,-81.09989
	gmt basemap -JM12c -R-81.2/-81.0/36.4/36.6 -Baf -BWSen #--FONT_TITLE=18P,Times-bold,black
	gmt grdimage @earth_relief_01s -R-81.2/-81.0/36.4/36.6 -I+d -Cgray -t40
	gmt colorbar -Bxaf+l"Elevation (m)"
	awk '{print $1,$2,$3,$4,$5,$6,$7}' ../../output/summarize_results.csv | gmt meca -Sa1.3c -Gred -t30
  echo -81.09989 36.48296 | gmt plot -Sa0.3c -Ggreen -W0.5p,black -l"mainshock"
  awk '{print $2,$1}' station.dat | gmt plot -St0.5c -Gblack -W0.5p,black -t30 -l"stations"
gmt end show