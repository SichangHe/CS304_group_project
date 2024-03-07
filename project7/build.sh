pandoc --pdf-engine xelatex \
    -V papersize=a4paper -V fontsize=12pt \
    -V geometry:margin=1in -V mainfont='Times' -V CJKmainfont='Songti TC' \
    -s project7_report.md -o project7_report.pdf
