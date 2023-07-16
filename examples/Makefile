executable = tabular2xls
tabellen_dir = tabellen

depends_ransomware_gehad=ransomware_gehad_gk_tabular.tex
targets_ransomware_gehad=$(tabellen_dir)/ransomware_gehad_gk_tabular.xlsx

depends_ransomware_losgeld=ransomware_losgeld_gk_tabular.tex
targets_ransomware_losgeld=$(tabellen_dir)/ransomware_losgeld_gk_tabular.xlsx

targets_ransomware = $(targets_ransomware_gehad) $(targets_ransomware_losgeld)

depends_cat_en_test=categorieen_en_testen_tabular.tex
targets_cat_en_test=$(tabellen_dir)/categorieen_en_testen_tabular.xlsx

depends_score_cate=score_categorieen_tabular.tex
targets_score_cat=$(tabellen_dir)/score_categorieen_tabular.xlsx

# scandata tabellen
depends_scandata=scan_data_tabular.tex
targets_scandata=$(tabellen_dir)/scan_data_tabular.xlsx

targets = $(targets_cat_en_test) $(targets_score_cat) $(targets_scandata) $(targets_ransomware)

depends = $(settings_file) $(depends_cat_en_test) $(depends_score_cate)

default: all

all: cat_en_test score_cat ransomware

ransomware_gehad: $(targets_ransomware_gehad)
$(targets_ransomware_gehad): $(depends_ransomware_gehad)
	$(executable) --top_row_merge $(depends_ransomware_gehad) --output_filename $(targets_ransomware_gehad)

ransomware_losgeld: $(targets_ransomware_losgeld)
$(targets_ransomware_losgeld): $(depends_ransomware_losgeld)
	$(executable) --top_row_merge $(depends_ransomware_losgeld) --output_filename $(targets_ransomware_losgeld)

ransomware: ransomware_losgeld ransomware_gehad

cat_en_test: $(targets_cat_en_test)
$(targets_cat_en_test): $(depends_cat_en_test)
	$(executable) $(depends_cat_en_test) --output_filename $(targets_cat_en_test)

score_cat: $(targets_score_cat)
$(targets_score_cat): $(depends_score_cate)
	$(executable) $(depends_score_cate) --output_filename $(targets_score_cat)

scandata: $(targets_scandata)
$(targets_scandata): $(depends_scandata)
	$(executable) $(options) $(depends_scandata) --output_filename $(targets_scandata) \
	--search_and_replace  Checkmark=Ja

clean:
	@$(foreach file, $(targets), test -f $(file) && rm -v $(file) || echo No $(file);)
