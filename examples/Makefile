executable = tabular2xls
tabellen_dir = tabellen

depends_cat_en_test=categorieen_en_testen_tabular.tex
targets_cat_en_test=$(tabellen_dir)/categorieen_en_testen_tabular.xlsx

depends_score_cate=score_categorieen_tabular.tex
targets_score_cat=$(tabellen_dir)/score_categorieen_tabular.xlsx

targets = $(targets_cat_en_test) $(targets_score_cat)

depends = $(settings_file) $(depends_cat_en_test) $(depends_score_cate)


default: all

all: cat_en_test score_cat

cat_en_test: $(targets_cat_en_test)
$(targets_cat_en_test): $(depends_cat_en_test)
	$(executable) $(depends_cat_en_test) --output_filename $(targets_cat_en_test)

score_cat: $(targets_score_cat)
$(targets_score_cat): $(depends_score_cate)
	$(executable) $(depends_score_cate) --output_filename $(targets_score_cat)


clean:
	@$(foreach file, $(targets), test -f $(file) && rm -v $(file) || echo No $(file);)
