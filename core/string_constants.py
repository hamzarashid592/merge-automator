class StringConstants:
    def __new__(cls):
        raise TypeError("Cannot instantiate static class")

    REGRESSION = "regression"
    PROD_SUPPORT = "production_support"

    TOKEN_PREFIX = "encrypted_tokens_"

    MANTIS_RESOLUTION_NEW = "New"
    MANTIS_RESOLUTION_FIXED = "Fixed"
    MANTIS_RESOLUTION_FOR_QA = "For QA"
    MANTIS_RESOLUTION_PARTIALLY_FIXED = "Partially Fixed"
    MANTIS_RESOLUTION_DOH = "Deployable on Hold"

    # Mantis Devs
    AADESH_KUMAR = 899
    ABID_ALI = 344
    AHSAN_RAZA = 861
    ALI_HASSAN = 1023
    DENNIS_RUFI = 1036
    HAMZA_RASHID = 795
    IBRAHIM_MUSTAFA = 825
    SYED_KHURRAM_KAMRAN = 969
    SYEDA_MOMINA_WASIQ = 763
    MUBASHIR_AHMED_SALEHEEN = 849
    MUHAMMAD_MOIZ_PATUJO = 887
    OWAIS_UL_HAQ = 843
    SHAHROZ_SHAHID_KHAN = 868
    SIMON_ANTHONY = 839
    MUHAMMAD_UMAIR_YOUSAF = 939
    MUHAMMAD_USAMA_HABIB_UR_REHMAN = 915
    USAMA_SAJID = 880
    ZUBAIR_AHMED = 914
    SYEDA_ZUNAIRA_AHMED = 756
    SYED_ZAIN_BADAR_UDDIN = 1038
    SYED_MOIZ_ISMAIL = 779

    # Mantis QAs
    ADEENA_SHAHAB = 'Adeena Shahab (QA)'
    ANUSHA_MAKHIJA = 'Anusha Makhija'
    GHULAM_SAKINA = 'Ghulam Sakina'
    HAFSA_YASEEN = 'Hafsa Yaseen (QA)'
    HAZIQ_JAMIL = 'Haziq Jamil'
    KAUSAR_TASNEEM = 'Kausar Tasneem (QA)'
    MUHAMMAD_ZEESHAN = 'Muhammad Zeeshan'
    QAZI_HAMZA_AHMED = 'Qazi Hamza Ahmed (QA)'
    SHABBIR_AHMED = 'Shabbir Ahmed (QA)'
    FARRUKH_FAHIM = ' Farrukh Fahim (QA)'
    NIMRA_IFTIKHAR = 'Nimra Iftikhar (QA)'
    RIMSHA_MOIN = 'Rimsha Moin'
    AMMAR_BHAI = 'Ammar Bin Ali Almanzar'