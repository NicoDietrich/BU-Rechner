# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
plt.ion()


class Versicherung:
    def __init__(self, versicherungs_settings):
        self.name = versicherungs_settings['name']
        self.passive_dynamik = versicherungs_settings['passive_dynamik']
        self.beitrags_dynamik = versicherungs_settings['beitrags_dynamik']
        self.inflationsausgleich = versicherungs_settings['inflationsausgleich']

        self.beitragsdynamik_interval = versicherungs_settings['beitragsdynamik_interval']
        self.monatsbeitrag_bu = versicherungs_settings['monatsbeitrag_bu']
        self.monatsbeitrag_rente = versicherungs_settings['monatsbeitrag_rente']
        self.leistung_bu = versicherungs_settings['leistung_bu']

        self.aktuelles_alter = 25
        self.renten_alter = 67

        self.rentenformel = versicherungs_settings['rentenformel']

        self.rentenvermoegen_evo = None
        self.bezahlt_bu_evo = None
        self.erhalten_bu_evo = None

        self.renten_beitragsevolution = None
        self.bu_beitragsevolution = None

        self.bu_monatsrentenevolution = None

    def init_evolutions(self):
        self.rentenvermoegen_evo = []
        self.bezahlt_bu_evo = []
        self.erhalten_bu_evo = []

        self.renten_beitragsevolution = []
        self.bu_beitragsevolution = []
        self.bu_monatsrentenevolution = []

    def update_evolutions(self, rente, bezahlt_bu, erhalten_bu, rentenbeitrag, bu_beitrag, bu_leistung):
        assert(self.rentenvermoegen_evo is not None)
        self.rentenvermoegen_evo.append(np.copy(rente))
        self.bezahlt_bu_evo.append(bezahlt_bu)
        self.erhalten_bu_evo.append(erhalten_bu)

        self.renten_beitragsevolution.append(rentenbeitrag)
        self.bu_beitragsevolution.append(bu_beitrag)
        self.bu_monatsrentenevolution.append(bu_leistung)

    def plot_rente(self):
        jahre = self.renten_alter - self.aktuelles_alter
        assert(self.rentenvermoegen_evo is not None)
        assert(len(self.rentenvermoegen_evo) == jahre)

        I = [i for i in range(jahre)]

        fig, ax = plt.subplots()
        rente = np.array(self.rentenvermoegen_evo)

        for index, fond_rate in enumerate(self.fond_entwicklung):
            ax.plot(I, rente[:, index],
                    label='fond rate: {}, vermoegen: {:.1f}, rente: {:.1f}'.format(
                        fond_rate, rente[-1, index], self.rentenformel(rente[-1, index])), marker='o')
            ax.grid(True)
            ax.set_title('{}: Rentenvermögen'.format(self.name))
        ax.legend(loc=0)

    def plot_bu_monatsrente(self):
        jahre = self.renten_alter - self.aktuelles_alter
        assert(self.bu_monatsrentenevolution is not None)
        assert(len(self.bu_monatsrentenevolution) == jahre)
        I = [i for i in range(jahre)]

        fig, ax = plt.subplots()
        ax.set_title('{}: BU Monatsrente'.format(self.name))
        ax.plot(I, self.bu_monatsrentenevolution, label='monatliche rente', marker='o')
        ax.grid(True)

    def plot_bu(self):
        jahre = self.renten_alter - self.aktuelles_alter
        assert(len(self.bezahlt_bu_evo) == jahre)
        I = [i for i in range(jahre)]
        fig, ax = plt.subplots()
        ax.plot(I, self.bezahlt_bu_evo, label='bezahlt bu', marker='o')
        ax.set_title('{}: BU Beiträge/Leistungen'.format(self.name))
        ax.plot(I, self.erhalten_bu_evo, label='erhalten bu', marker='o')
        ax.grid(True)

    def plot_beitraege(self):
        jahre = self.renten_alter - self.aktuelles_alter
        assert(self.renten_beitragsevolution is not None)
        assert(len(self.renten_beitragsevolution) == jahre)

        I = [i for i in range(jahre)]
        fig, ax = plt.subplots()
        ax.set_title('{}: Monatsbeiträge im jahr'.format(self.name))
        ax.plot(I, self.renten_beitragsevolution, label='Rente', marker='o')
        ax.plot(I, self.bu_beitragsevolution, label='BU', marker='o')
        ax.grid(True)
        ax.legend()

    def simulate(self, bu_alter,
                 fond_entwicklung=[0.02, 0.03, 0.04, 0.05, 0.06]):
        fond_entwicklung = np.array(fond_entwicklung)
        self.fond_entwicklung = fond_entwicklung
        print("\n-------------------{}---------------------".format(self.name))
        print("Starte Simulation mit Rentenalter {}".format(bu_alter))
        beitragsjahre = bu_alter - self.aktuelles_alter
        bu_leistungsjahre = self.renten_alter - bu_alter

        monatsbeitrag_rente = self.monatsbeitrag_rente
        monatsbeitrag_bu = self.monatsbeitrag_bu
        leistung_bu = self.leistung_bu

        rentenvermoegen = 0
        bezahlt_bu = 0
        erhalten_bu = 0

        self.init_evolutions()

        print("Berechne {} Beitragsjahre".format(beitragsjahre))
        for i in range(beitragsjahre):
            rentenvermoegen *= 1 + fond_entwicklung
            rentenvermoegen += 12*monatsbeitrag_rente
            bezahlt_bu += 12*monatsbeitrag_bu

            if i % 3 == 2:
                monatsbeitrag_rente *= 1 + self.beitrags_dynamik
                monatsbeitrag_bu *= 1 + self.beitrags_dynamik
                leistung_bu *= 1 + self.beitrags_dynamik

            self.update_evolutions(rentenvermoegen, bezahlt_bu, erhalten_bu, monatsbeitrag_rente,
                                   monatsbeitrag_bu, leistung_bu)

        print("Berechne {} Leistungsjahre".format(bu_leistungsjahre))

        monatsbeitrag_bu = 0
        for i in range(bu_leistungsjahre):
            erhalten_bu += 12*leistung_bu
            rentenvermoegen *= 1 + fond_entwicklung
            rentenvermoegen += 12*monatsbeitrag_rente

            leistung_bu *= 1 + self.inflationsausgleich

            monatsbeitrag_rente *= 1 + self.passive_dynamik

            self.update_evolutions(rentenvermoegen, bezahlt_bu, erhalten_bu, monatsbeitrag_rente,
                                   monatsbeitrag_bu, leistung_bu)

        print("-------------------------------------------")
        print("BU Beitrag: {}\nBU Leistungen: {}\nRentenvermögen: {}".format(bezahlt_bu, erhalten_bu,
                                                                             rentenvermoegen))
        print("Monatsrenten:", [self.rentenformel(vermoegen) for vermoegen in rentenvermoegen])


alte_leipziger = {
    'name': 'AL',
    'passive_dynamik': 0.05,
    'beitrags_dynamik': 0.03,
    'inflationsausgleich': 0.02,

    'beitragsdynamik_interval': 3,  # alle X Jahre;

    'monatsbeitrag_bu': 72.55,
    'monatsbeitrag_rente': 30.49,
    'leistung_bu': 1500,
    'rentenformel': lambda x: x/10000*21.47
}

# Beitrag wird mit 3% angepasst, BU leistung mir 2.5 ?????

volkswohlbund = {
    'name': 'VW',
    'passive_dynamik': 0.10,
    'beitrags_dynamik': 0.03,
    'inflationsausgleich': 0.015,

    'beitragsdynamik_interval': 3,  # alle X Jahre;

    'monatsbeitrag_bu': 63.13,
    'monatsbeitrag_rente': 39.87,
    'leistung_bu': 1500,
    'rentenformel': lambda x: x/10000*21.52
}

if __name__ == '__main__':
    al = Versicherung(alte_leipziger)
    vw = Versicherung(volkswohlbund)
    bu_alter = 45
    fond_entwicklung = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
    al.simulate(bu_alter, fond_entwicklung)
    vw.simulate(bu_alter, fond_entwicklung)
