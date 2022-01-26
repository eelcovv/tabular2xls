import nose
import pandas as pd
import numpy as np
import pandas.testing as pt
import numpy.testing as nt

from tabular2xls.tabular_convert_tool import parse_tabular


def test_tabular_1():
    """API Tests"""
    tabular_df = parse_tabular(input_filename='tabular_1.tex')

    expected_column_names = pd.Index(['Testomschrijving', 'Testuitkomsten', 'Variabelenaam'])
    expected_index = pd.Index(
        ['IPv6', '', '', '', '', 'DNSSEC', '', 'HTTPS', '', '', '', '', '', '', '', '', '', '', '',
         '', '', '', '', '', '', '', '', '', 'opties', '', ''], name="Categorie")
    expected_columns = dict(
        Testomschrijving=np.array(['IPv6-adressen voor nameservers',
                                   'IPv6-bereikbaarheid van nameservers',
                                   'IPv6-adressen voor webserver',
                                   'IPv6-bereikbaarheid van webservers',
                                   'Gelijke website op IPv6 en IPv4', 'DNSSEC aanwezig',
                                   'DNSSEC geldigheid', 'HTTPS beschikbaar', 'HTTPS-doorverwijzing',
                                   'HTTPS-compressie', 'HSTS aangeboden', 'TLS Versie',
                                   'TLS ciphers',
                                   'TLS cipher-volgorde', 'TLS sleuteluitwisselingsparameters',
                                   'Hashfunctie voor sleuteluitwisseling', 'TLS-compressie',
                                   'Secure renegotiation', 'Client initiated renegotiation',
                                   '0-RTT',
                                   'TLS OCSP-stapeling', 'Vertrouwensketen van certificaat',
                                   'Publieke sleutel van certificaat',
                                   'Handtekening van certificaat',
                                   'Domeinnaam op certificaat', 'DANE aanwezig', 'DANE geldigheid',
                                   'X-Frame-options', 'X-Content-Type-Options',
                                   'Content-Security-Policy', 'Referrer-Policy aanwezig'],
                                  dtype=object),
        Testuitkomsten=np.array(['good/bad/other', 'good/bad/not tested', 'good/bad',
                                 'good/bad/not tested', 'good/bad/not tested',
                                 'good/bad/server failed', 'good/bad/not tested', 'good/bad/other',
                                 'good/bad/other/not tested', 'good/bad/not tested',
                                 'good/bad/other/not tested', 'good/bad/phase out/not tested',
                                 'good/bad/phase out/not tested', 'good/bad/other/not tested',
                                 'good/bad/phase out/not tested', 'good/bad/phase out/not tested',
                                 'good/bad/not tested', 'good/bad/not tested',
                                 'good/bad/not tested', 'good/bad/N.A./not tested',
                                 'good/ok/bad/not tested', 'good/bad/not tested',
                                 'good/bad/not tested', 'good/bad/not tested',
                                 'good/bad/not tested', 'good/bad/not tested',
                                 'good/bad/not tested', 'good/bad/phase out/not tested',
                                 'good/bad/phase out/not tested', 'good/bad/not tested',
                                 'good/bad/not tested'], dtype=object),
        Variabelenaam=np.array(['tests_web_ipv6_ns_address_verdict',
                                'tests_web_ipv6_ns_reach_verdict',
                                'tests_web_ipv6_ws_address_verdict',
                                'tests_web_ipv6_ws_reach_verdict',
                                'tests_web_ipv6_ws_similar_verdict',
                                'tests_web_dnssec_exist_verdict', 'tests_web_dnssec_valid_verdict',
                                'tests_web_https_http_available_verdict',
                                'tests_web_https_http_redirect_verdict',
                                'tests_web_https_http_compress_verdict',
                                'tests_web_https_http_hsts_verdict',
                                'tests_web_https_tls_version_verdict',
                                'tests_web_https_tls_ciphers_verdict',
                                'tests_web_https_tls_cipherorder_verdict',
                                'tests_web_https_tls_keyexchange_verdict',
                                'tests_web_https_tls_keyexchangehash_verdict',
                                'tests_web_https_tls_compress_verdict',
                                'tests_web_https_tls_secreneg_verdict',
                                'tests_web_https_tls_clientreneg_verdict',
                                'tests_web_https_tls_0rtt_verdict',
                                'tests_web_https_tls_ocsp_verdict',
                                'tests_web_https_cert_chain_verdict',
                                'tests_web_https_cert_pubkey_verdict',
                                'tests_web_https_cert_sig_verdict',
                                'tests_web_https_cert_domain_verdict',
                                'tests_web_https_dane_exist_verdict',
                                'tests_web_https_dane_valid_verdict',
                                'tests_web_appsecpriv_x_frame_options_verdict',
                                'tests_web_appsecpriv_x_content_type_options_verdict',
                                'tests_web_appsecpriv_csp_verdict',
                                'tests_web_appsecpriv_referrer_policy_verdict'], dtype=object)
    )

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)

    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        nt.assert_array_equal(tabular_df[column_name].to_numpy(), expected_col)


def test_tabular_2():
    """API Tests"""
    tabular_df = parse_tabular(input_filename='tabular_2.tex')

    expected_column_names = pd.Index(['2008-2013', '2014-2019 ¹⁾'], dtype='object')

    expected_index = pd.Index([('Totaal door OM genomen beslissingen', ''),
                               ('', '- waaronder strafoplegging OM²⁾'),
                               ('Schuldig verklaard door rechter', '')],
                              dtype='object', name='', tupleize_cols=False)

    expected_columns = {
        "2008-2013": np.array(['512', '93', '124'], dtype=object),
        "2014-2019 ¹⁾": np.array(['551', '88', '82'], dtype=object)
    }

    pt.assert_index_equal(tabular_df.columns, expected_column_names)
    pt.assert_index_equal(tabular_df.index, expected_index)
    for column_name in expected_column_names:
        expected_col = expected_columns[column_name]
        nt.assert_array_equal(tabular_df[column_name].to_numpy(), expected_col)

