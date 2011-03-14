#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from cocktail.translations import translations

# Sign up Page
translations.define("SignUpPage",
    ca = u"Pàgina d'alta d'usuari",
    es = u"Página de alta de usuario",
    en = u"Sign up page"
)

translations.define("SignUpPage-plural",
    ca = u"Pàgines d'alta d'usuari",
    es = u"Páginas de alta de usuario",
    en = u"Sign up pages"
)

translations.define("SignUpPage.signup_process",
    ca = u"Procés d'alta",
    es = u"Proceso de alta",
    en = u"Sign up process"
)

translations.define("SignUpPage.user_type",
    ca = u"Tipus d'usuari",
    es = u"Tipo de usuario",
    en = u"User type"
)

translations.define("SignUpPage.roles",
    ca = u"Rols per defecte",
    es = u"Roles por defecto",
    en = u"Default roles"
)

translations.define("SignUpPage.roles-explanation",
    ca = u"Rols que seran assignats després de l'alta",
    es = u"Roles que serán asigandos tras el alta",
    en = u"Roles that will be assigned after sign up"
)

translations.define("SignUpPage.confirmation_target",
    ca = u"Document de confirmació",
    es = u"Documento de confirmación",
    en = u"Confirmation document"
)

translations.define("SignUpPage.confirmation_target-explanation",
    ca = u"Document on finalitza el procés d'alta i es gestiona la confirmació si correspon",
    es = u"Documento donde finaliza el proceso de alta y se gestiona la confirmación si corresponde",
    en = u"Document where ends the sign up process and will be take place the sign up confirmation process if is required"
)

translations.define("SignUpPage.confirmation_email_template",
    ca = u"Plantilla de correu electrònic de confirmació",
    es = u"Plantilla de correo electrónico de confirmación",
    en = u"Sign up email template"
)

translations.define("SignUpPage.confirmation_email_template-explanation",
    ca = u"""Assignar una plantilla de correu electrònic de confirmació activa
        automàticament el sistema de confirmació per correu electrònic en el
        procés d'alta.""",
    es = u"""Asignar una plantilla de email de confirmación, activa
        automáticamente el sistema de confirmación por email en el proceso de
        alta""",
    en = u"""Selecting a sign up email template will automatically enable the 
        email confirmation system in the sign up process"""
)

translations.define("SignUpForm.password_confirmation",
    ca = u"Confirmar la contrasenya",
    es = u"Confirmar la contraseña",
    en = u"Confirm password",
    pt = u"Confirmar Palavra-passe"
)

translations.define("woost.extensions.signup.SignupSuccessfulMessage",
    ca = u"Alta realitzada amb èxit.",
    es = u"Alta realizada con éxito.",
    en = u"Thanks for signing up!"
)
translations.define("woost.extensions.signup.SignupConfirmationMessageNotice",
    ca = u"""
        En breu rebrà un missatge a la bústia de 
        correu electrònic que ens ha facilitat. Segueixi les indicacions del
        correu per tal de confirmar la seva alta a la web. Gràcies.
    """,
    es = u"""
        En breve recibirá un mensaje en el buzón de
        correo electrónico que nos ha indicado. Siga los pasos que allí le
        indicamos para que confirme su alta en la web. Gracias.
    """,
    en = u"""
        We've sent you an email with the necessary
        instructions to complete the registration process.
    """
)

translations.define("woost.extensions.signup.SignupSuccessfulConfirmationMessage",
    ca = u"Alta d'usuari confirmada correctament!",
    es = u"Alta de usuario confirmada correctamente!",
    en = u"Sign up correctly confirmed"
)

translations.define("woost.extensions.signup.SignupFailConfirmationMessage",
    ca = u"Confirmació fallida",
    es = u"Fallo en proceso de confirmación.",
    en = u"Confirmation failure"
)

# User
#------------------------------------------------------------------------------
translations.define("User.confirmed_email",
    ca = u"Correu electrònic confirmat",
    es = u"Correo electrónico confirmado",
    en = u"Confirmed email"
)
