# -*- coding: utf-8 -*-
"""
    pidsim_models.models
    ~~~~~~~~~~~~~~~~~~~~

    Models implementation.

    :copyright: 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from pidsim.approximation import methods
from pidsim.types import tf, poly
from pidsim_models.base import ReferenceModel, I18nStr

class Model1(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de primeira ordem'),
        ('en_US', u'First order model'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são o ganho estático (k) e a constante de tempo
(Tau)'''),
        ('en_US', u'''\
The model parameters are the static gain (k) and the time constant (Tau)'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{k}{(1+\\tau s)}'
    
    def callback(self, k, Tau):
        return tf([k], [Tau, 1])


class Model2(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de segunda ordem'),
        ('en_US', u'Second order model'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são o ganho estático (k) e os tempos T1 e T2.'''),
        ('en_US', u'''\
The model parameters are the static gain (k) and the times T1 and T2.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{k}{(1+T_1 s)(1+T_2 s)}'
    
    def callback(self, k, T1, T2):
        return tf([k], poly([T1, 1]) * poly([T2, 1]))


class Model3(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de segunda ordem de fase não-mínima'),
        ('en_US', u'Second order model of non-minimal phase')
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são o ganho estático (k) e os tempos T1 e T2.'''),
        ('en_US', u'''\
The model parameters are the static gain (k) and the times T1 and T2.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{k(1-T_1 s)}{(1+T_1 s)(1+T_2 s)}'
    
    def callback(self, k, T1, T2):
        return tf([-T1 * k, k], poly([T1, 1]) * poly([T2, 1]))


class Model4(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de terceira ordem com tempo morto ajustável'),
        ('en_US', u'Third order model with adjustable dead time')
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são o ganho estático (k), os tempos T1, T2, T3 e T4,
o tempo morto (Tt) e a ordem da aproximação de Padé, utilizada para simular
o tempo morto.'''),
        ('en_US', u'''\
The model parameters are the static gain (k), the times T1, T2, T3 and T4,
the dead time (Tt) and the Padé approximant order, used to simulate the
dead time.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{k(1+T_4 s)}{(1+T_1 s)(1+T_2 s)(1+T_3 s)} e^{-T_t s}'
    
    def callback(self, k, T1, T2, T3, T4, Tt, pade_order):
        num = poly([k * T4, k])
        den = poly([T1, 1]) * poly([T2, 1]) * poly([T3, 1])
        return tf(num, den) * methods[int(pade_order)](Tt)


class Model5(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de pólos múltiplos e iguais'),
        ('en_US', u'Model with multiple equal poles'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'''
O único parâmetro do processo é a sua ordem (n). Os valores sugeridos
para n são: 1, 2, 3, 4 e 8.'''),
        ('en_US', u'''
The unique parameter of the model is its order (n). The suggested values
for n are: 1, 2, 3, 4 and 8.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1}{(s+1)^n}'
    
    def callback(self, n):
        a = poly([1, 1])
        for i in range(1, int(n)):
            a = a * poly([1, 1])
        return tf([1], list(a))


class Model6(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de quarta ordem'),
        ('en_US', u'Fourth order model'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
O único parâmetro do processo é o Alpha. Os valores sugeridos para o
Alpha são: 0.1, 0.2, 0.5 e 1.'''),
        ('en_US', u'''\
The unique parameter of the model is Alpha. The suggested values for
Alpha are: 0.1, 0.2, 0.5 and 1.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1}{(s+1)(\\alpha s+1)(\\alpha ^2 s+1)(\\alpha ^3 s+1)}'
    
    def callback(self, Alpha):
        num = (poly([1, 1]) * poly([Alpha, 1])) * (poly([Alpha * Alpha, 1]) * \
            poly([Alpha * Alpha * Alpha, 1]))
        return tf([1], num)


class Model7(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo com três pólos iguais e zero no semi-plano direito'),
        ('en_US', u'Model with three equal poles and zero at the right half-plane'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
O único parâmetro do processo é o Alpha. Os valores sugeridos para o
Alpha são: 0.1, 0.2, 0.5, 1, 2 e 5.'''),
        ('en_US', u'''\
The unique parameter of the model is Alpha. The suggested values for
Alpha are: 0.1, 0.2, 0.5, 1, 2 and 5.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1-\\alpha s}{(s+1)^3}'
    
    def callback(self, Alpha):
        return tf([-Alpha, 1], (poly([1, 1]) * poly([1, 1])) * poly([1, 1]))


class Model8(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de primeira ordem com tempo morto'),
        ('en_US', u'First order model with dead time')
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são a constante de tempo (Tau) e a ordem da
aproximação de Padé, utilizada para simular o tempo morto.'''),
        ('en_US', u'''\
The model parameters are the time constant (Tau) and the Padé approximant
order, used to simulate the dead time.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1}{(\\tau s +1)}e^{-s}'
    
    def callback(self, Tau, pade_order):
        return tf([1], [Tau, 1]) * methods[int(pade_order)](1)


class Model9(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de segunda ordem com tempo morto'),
        ('en_US', u'Second order model with dead time')
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são a constante de tempo (Tau) e a ordem da
aproximação de Padé, utilizada para simular o tempo morto.'''),
        ('en_US', u'''\
The model parameters are the time constant (Tau) and the Padé approximant
order, used to simulate the dead time.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1}{(\\tau s +1)^2}e^{-s}'
    
    def callback(self, Tau, pade_order):
        return tf([1], poly([Tau, 1]) * poly([Tau, 1])) * \
            methods[int(pade_order)](1)


class Model10(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo com características dinâmicas assimétricas'),
        ('en_US', u'Model with asymmetric dynamic caracteristics')
    ])
    
    description = I18nStr([
        ('pt_BR', u'Este processo não permite parametrização.'),
        ('en_US', u'This model does not allow parameterization.'),
    ])
    
    transfer_function = 'G_p(s) = \\frac{100}{(s+10)^2}\\left ( \\frac{1}{s+1} + \\frac{0,5}{s+0,05} \\right )'
    
    def callback(self):
        p1 = tf([100], poly([1, 10]) * poly([1, 10]))
        p2 = tf([1], [1, 1])
        p3 = tf([0.5], [1, 0.05])
        return p1 * (p2 + p3)


class Model11(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo condicionalmente estável'),
        ('en_US', u'Conditionally stable model'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'Este processo não permite parametrização.'),
        ('en_US', u'This model does not allow parameterization.'),
    ])
    
    transfer_function = 'G_p(s) = \\frac{(s+6)^2}{s(s+1)^2 (s+36)}'
    
    def callback(self):
        den = (poly([1, 0]) * poly([1, 1])) * (poly([1, 1]) * poly([1, 36]))
        return tf(poly([1, 6]) * poly([1, 6]), den)


class Model12(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo oscilatório'),
        ('en_US', u'Oscillating model'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são o Omega e o Zeta. Os valor sugerido para
Zeta é 0.1 e os valores sugeridos para Omega são 1, 2, 5 e 10.'''),
        ('en_US', u'''\
The model parameters are Omega and Zeta. The suggested value for Zeta
is 0.1 and the suggested values for Omega are 1, 2, 5 and 10.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{\\omega _0^2}{(s+1)(s^2+2\\zeta \\omega _0 s+\\omega _0^2)}'
    
    def callback(self, Omega, Zeta):
        return tf([Omega * Omega], poly([1, 1]) * poly([1, 2 * Zeta * Omega, Omega * Omega]))


class Model13(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo instável'),
        ('en_US', u'Unstable model'),
    ])
    
    description = I18nStr([
        ('pt_BR', u'Este processo não permite parametrização.'),
        ('en_US', u'This model does not allow parameterization.'),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1}{s^2 - 1}'
    
    def callback(self):
        return tf([1], [1, 0, -1])


class Model14(ReferenceModel):
    
    name = I18nStr([
        ('pt_BR', u'Processo de primeira ordem mais tempo morto com a presença de integrador'),
        ('en_US', u'Second order plus dead time model with presence of integrator')
    ])
    
    description = I18nStr([
        ('pt_BR', u'''\
Os parâmetros do processo são a constante de tempo (Tau) e a ordem da
aproximação de Padé, utilizada para simular o tempo morto.'''),
        ('en_US', u'''\
The model parameters are the time constant (Tau) and the Padé approximant
order, used to simulate the dead time.'''),
    ])
    
    transfer_function = 'G_p(s) = \\frac{1}{s(\\tau s + 1)}e^{-s}'
    
    def callback(self, Tau, pade_order):
        return tf([1], [Tau, 1, 1]) * methods[int(pade_order)](1)

index = {
    1: Model1,
    2: Model2,
    3: Model3,
    4: Model4,
    5: Model5,
    6: Model6,
    7: Model7,
    8: Model8,
    9: Model9,
    10: Model10,
    11: Model11,
    12: Model12,
    13: Model13,
    14: Model14,
}
