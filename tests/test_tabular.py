from pathlib import Path
import pandas as pd
import numpy as np
import pandas.testing as pt
import numpy.testing as nt

from tabularxls.main import parse_tabular


def get_root_directory():
    """small utility to get the root directory from which pytests is launched"""
    current_directory = Path(".").cwd().name
    if current_directory == "tests":
        # we are inside the tests-directory. Move one up
        root_directory = Path("..")
    else:
        # we are in the root directory
        root_directory = Path(".")
    return root_directory


def test_tabular_1():
    """API Tests"""
    root = get_root_directory()

    tabular_file = root / Path("tests/tabular_1.tex")
    tabular_df = parse_tabular(input_filename=tabular_file)

    expected_column_names = pd.Index(
        ["Testomschrijving", "Testuitkomsten", "Variabelenaam"]
    )
    expected_index = pd.Index(
        [
            "IPv6",
            "",
            "",
            "",
            "",
            "DNSSEC",
            "",
            "HTTPS",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "opties",
            "",
            "",
        ],
        name="Categorie",
    )
    expected_columns = dict(
        Testomschrijving=np.array(
            [
                "IPv6-adressen voor nameservers",
                "IPv6-bereikbaarheid van nameservers",
                "IPv6-adressen voor webserver",
                "IPv6-bereikbaarheid van webservers",
                "Gelijke website op IPv6 en IPv4",
                "DNSSEC aanwezig",
                "DNSSEC geldigheid",
                "HTTPS beschikbaar",
                "HTTPS-doorverwijzing",
                "HTTPS-compressie",
                "HSTS aangeboden",
                "TLS Versie",
                "TLS ciphers",
                "TLS cipher-volgorde",
                "TLS sleuteluitwisselingsparameters",
                "Hashfunctie voor sleuteluitwisseling",
                "TLS-compressie",
                "Secure renegotiation",
                "Client initiated renegotiation",
                "0-RTT",
                "TLS OCSP-stapeling",
                "Vertrouwensketen van certificaat",
                "Publieke sleutel van certificaat",
                "Handtekening van certificaat",
                "Domeinnaam op certificaat",
                "DANE aanwezig",
                "DANE geldigheid",
                "X-Frame-options",
                "X-Content-Type-Options",
                "Content-Security-Policy",
                "Referrer-Policy aanwezig",
            ],
            dtype=object,
        ),
        Testuitkomsten=np.array(
            [
                "good/bad/other",
                "good/bad/not tested",
                "good/bad",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/server failed",
                "good/bad/not tested",
                "good/bad/other",
                "good/bad/other/not tested",
                "good/bad/not tested",
                "good/bad/other/not tested",
                "good/bad/phase out/not tested",
                "good/bad/phase out/not tested",
                "good/bad/other/not tested",
                "good/bad/phase out/not tested",
                "good/bad/phase out/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/N.A./not tested",
                "good/ok/bad/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
                "good/bad/phase out/not tested",
                "good/bad/phase out/not tested",
                "good/bad/not tested",
                "good/bad/not tested",
            ],
            dtype=object,
        ),
        Variabelenaam=np.array(
            [
                "tests_web_ipv6_ns_address_verdict",
                "tests_web_ipv6_ns_reach_verdict",
                "tests_web_ipv6_ws_address_verdict",
                "tests_web_ipv6_ws_reach_verdict",
                "tests_web_ipv6_ws_similar_verdict",
                "tests_web_dnssec_exist_verdict",
                "tests_web_dnssec_valid_verdict",
                "tests_web_https_http_available_verdict",
                "tests_web_https_http_redirect_verdict",
                "tests_web_https_http_compress_verdict",
                "tests_web_https_http_hsts_verdict",
                "tests_web_https_tls_version_verdict",
                "tests_web_https_tls_ciphers_verdict",
                "tests_web_https_tls_cipherorder_verdict",
                "tests_web_https_tls_keyexchange_verdict",
                "tests_web_https_tls_keyexchangehash_verdict",
                "tests_web_https_tls_compress_verdict",
                "tests_web_https_tls_secreneg_verdict",
                "tests_web_https_tls_clientreneg_verdict",
                "tests_web_https_tls_0rtt_verdict",
                "tests_web_https_tls_ocsp_verdict",
                "tests_web_https_cert_chain_verdict",
                "tests_web_https_cert_pubkey_verdict",
                "tests_web_https_cert_sig_verdict",
                "tests_web_https_cert_domain_verdict",
                "tests_web_https_dane_exist_verdict",
                "tests_web_https_dane_valid_verdict",
                "tests_web_appsecpriv_x_frame_options_verdict",
                "tests_web_appsecpriv_x_content_type_options_verdict",
                "tests_web_appsecpriv_csp_verdict",
                "tests_web_appsecpriv_referrer_policy_verdict",
            ],
            dtype=object,
        ),
    )

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)

    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        nt.assert_array_equal(tabular_df[column_name].to_numpy(), expected_col)


def test_tabular_2():
    """API Tests"""
    root = get_root_directory()

    tabular_file = root / Path("tests/tabular_2.tex")
    tabular_df = parse_tabular(input_filename=tabular_file, multi_index=True)

    expected_column_names = pd.Index(["2008-2013", "2014-2019 ¹⁾"], dtype="object")

    expected_index = pd.Index(
        [
            ("Totaal door OM genomen beslissingen", ""),
            ("", "- waaronder strafoplegging OM²⁾"),
            ("Schuldig verklaard door rechter", ""),
        ],
        dtype="object",
    )
    expected_index = expected_index.rename(["", ""])

    expected_columns = {
        "2008-2013": np.array(["512", "93", "124"], dtype=object),
        "2014-2019 ¹⁾": np.array(["551", "88", "82"], dtype=object),
    }

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)
    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        nt.assert_array_equal(tabular_df[column_name].to_numpy(), expected_col)


def test_tabular_3():
    """API Tests"""
    root = get_root_directory()

    tabular_file = root / Path("tests/tabular_3.tex")
    tabular_df = parse_tabular(input_filename=tabular_file)

    expected_column_names = pd.Index(["Bedrijfsklasse"], dtype="object")

    expected_index = pd.Index(
        ["C", "D-E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "Q", "ICT"],
        dtype="object",
    )
    expected_index = expected_index.rename("Code")

    expected_columns = {
        "Bedrijfsklasse": np.array(
            [
                "Industrie",
                "Energie, water, afvalbeheer",
                "Bouwnijverheid",
                "Handel",
                "Vervoer en opslag",
                "Horeca",
                "Informatie en communicatie",
                "Financiële dienstverlening",
                "Verhuur en handel van onroerend goed",
                "Specialistische zakelijke diensten",
                "Verhuur en overige zakelijke diensten",
                "Gezondheids- en welzijnszorg",
                "ICT-sector",
            ],
            dtype=object,
        )
    }

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)
    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        tabular_col = tabular_df[column_name].to_numpy()
        nt.assert_array_equal(tabular_col, expected_col)


def test_tabular_4():
    """API Tests"""

    root = get_root_directory()

    tabular_file = root / Path("tests/tabular_4.tex")
    tabular_df = parse_tabular(input_filename=tabular_file)

    expected_column_names = pd.Index(["Bedrijfsgrootte"], dtype="object")

    expected_index = pd.Index(
        [
            "Totaal",
            "2-250",
            "2",
            "3-5",
            "5-10",
            "10-20",
            "20-50",
            "50-100",
            "100-250",
            "250-500",
            "500+",
        ],
        dtype="object",
    )
    expected_index = expected_index.rename("Code")

    expected_columns = {
        "Bedrijfsgrootte": np.array(
            [
                "2 of meer werkzame personen",
                "2 tot 250 werkzame personen",
                "2 werkzame personen",
                "3 tot 5 werkzame personen",
                "5 tot 10 werkzame personen",
                "10 tot 20 werkzame personen",
                "20 tot 50 werkzame personen",
                "50 tot 100 werkzame personen",
                "100 tot 250 werkzame personen",
                "250 tot 500 werkzame personen",
                "500 of meer werkzame personen",
            ],
            dtype=object,
        )
    }

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)
    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        nt.assert_array_equal(tabular_df[column_name].to_numpy(), expected_col)


def test_tabular_5():
    """API Tests"""
    # let op dat de cdot en ast commando's zonder \ gegeven worden omdat we search en replace
    # op het eind pas toepassen en dan zijn alle back slashes al verwijderd
    s_and_r = {
        r"\$cdot\$": ".",
        r"\$ast\$": "*",
    }
    root = get_root_directory()

    tabular_file = root / Path("tests/tabular_5.tex")
    tabular_df = parse_tabular(input_filename=tabular_file, search_and_replace=s_and_r)

    expected_column_names = pd.Index(
        ["Pilot 2015", "Onderzoek 2017", "Onderzoek 2019", "Opmerkingen"],
        dtype="object",
    )

    expected_index = pd.Index(
        [
            "Disciplines culturele en creatieve sector",
            "Aantallen instellingen en bedrijven incl. zelfstandigen",
            "Regionale verdeling van instellingen en bedrijven",
            "Disciplines cultuureducaties sec (scholing)",
            "Artistieke begeleiding amateurgezelschappen",
            "Ondersteuning en advisering cultuureducatie",
            "Hoe leerlingen zijn aangemeld",
            "Hoe leerlingen zijn geworven",
            "Aantallen leerlingen / doelgroepen",
            "Geografisch servicegebied",
            "Financiële gegevens (baten en lasten)",
            "Werkgelegenheid",
            "Subsidie",
            "Samenwerking met andere bedrijven en instellingen",
            "Verwachtingen voor het volgend seizoen/jaar",
        ],
        dtype="object",
        name="Onderwerp",
    )
    expected_index = expected_index.rename("Onderwerp")

    expected_columns = {
        "Pilot 2015": np.array(
            [".", "*", "*", "*", ".", "*", "*", ".", "*", ".", ".", ".", "*", "*", "*"],
            dtype="object",
        ),
        "Onderzoek 2017": np.array(
            ["*", "*", "*", "*", ".", "*", "*", ".", "*", "*", "*", "*", "*", "*", "*"],
            dtype="object",
        ),
        "Onderzoek 2019": np.array(
            ["*", "*", "*", "*", "*", "*", ".", "*", "*", "*", "*", "*", "*", "*", "."],
            dtype="object",
        ),
        "Opmerkingen": np.array(
            [
                "In deze rapportage verder buiten beschouwing gelaten",
                "In deze rapportage is gekeken naar alle eenheden van de betreffende SBI's",
                "Adresgegevens zijn beschikbaar als gevolg van de steekproef uit het ABR",
                "",
                "",
                "",
                "",
                "",
                "Per onderzoek zijn verschillende categoriën gehanteerd",
                "In welke gemeenten of provincies wordt cultuureducatie aangeboden? Tussen 2017 en 2019 was er wel een verschil in vraagstelling",
                "Zie standaardvraagstelling CBS. Beperkt bij zelfstandigen",
                "Zie standaardvraagstelling CBS. Beperkt bij zelfstandigen",
                "In 2017 en 2019 veel uitgebreider dan in 2015. Toen is alleen gevraagd of er wel of geen sprake was van subsidies.",
                "",
                "",
            ],
            dtype="object",
        ),
    }

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)
    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        nt.assert_array_equal(tabular_df[column_name].to_numpy(), expected_col)
