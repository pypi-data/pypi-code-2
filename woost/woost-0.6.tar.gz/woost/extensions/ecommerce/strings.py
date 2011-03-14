#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.translations import translations, DATE_STYLE_TEXT
from cocktail.translations.helpers import plural2

# ECommerceExtension
#------------------------------------------------------------------------------
translations.define("ECommerceExtension.pricing",
    ca = u"Preus",
    es = u"Precios",
    en = u"Pricing"
)

translations.define("ECommerceExtension.shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs"
)

translations.define("ECommerceExtension.taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes"
)

translations.define("ECommerceExtension.order_steps",
    ca = u"Passos de la compra",
    es = u"Pasos de la compra",
    en = u"Order steps"
)

# ECommerceProduct
#------------------------------------------------------------------------------
translations.define("ECommerceProduct",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("ECommerceProduct-plural",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products"
)

translations.define("ECommerceProduct.product_data",
    ca = u"Dades del producte",
    es = u"Datos del producto",
    en = u"Product data"
)

translations.define("ECommerceProduct.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("ECommerceProduct.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("ECommerceProduct.weight",
    ca = u"Pes",
    es = u"Peso",
    en = u"Weight"
)

translations.define("ECommerceProduct.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

translations.define("ECommerceProduct.purchase_model",
    ca = u"Model de compra",
    es = u"Modelo de compra",
    en = u"Purchase model"
)

translations.define("ECommerceProduct.purchases",
    ca = u"Compres",
    es = u"Compras",
    en = u"Purchases"
)

translations.define("ECommerceProduct.template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template"
)

# ECommerceOrder
#------------------------------------------------------------------------------
translations.define("ECommerceOrder",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Shop order"
)

translations.define("ECommerceOrder-plural",
    ca = u"Comandes",
    es = u"Pedidos",
    en = u"Shop orders"
)

translations.define("ECommerceOrder.customer",
    ca = u"Client",
    es = u"Cliente",
    en = u"Customer"
)

translations.define("ECommerceOrder.shipping_info",
    ca = u"Direcció d'enviament",
    es = u"Dirección de envío",
    en = u"Shipping address"
)

translations.define("ECommerceOrder.address",
    ca = u"Adreça",
    es = u"Dirección",
    en = u"Address"
)

translations.define("ECommerceOrder.town",
    ca = u"Població",
    es = u"Población",
    en = u"Town"
)

translations.define("ECommerceOrder.region",
    ca = u"Estat o província",
    es = u"Estado o provincia",
    en = u"State or province"
)

translations.define("ECommerceOrder.country",
    ca = u"País",
    es = u"País",
    en = u"Country"
)

translations.define("ECommerceOrder.postal_code",
    ca = u"Codi postal",
    es = u"Código postal",
    en = u"Postal code"
)

translations.define("ECommerceOrder.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("ECommerceOrder.status",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

translations.define("ECommerceOrder.status-shopping",
    ca = u"En curs",
    es = u"En curso",
    en = u"Shopping"
)

translations.define("ECommerceOrder.status-payment_pending",
    ca = u"Pendent de pagament",
    es = u"Pago pendiente",
    en = u"Payment pending"
)

translations.define("ECommerceOrder.status-accepted",
    ca = u"Acceptada",
    es = u"Aceptada",
    en = u"Accepted"
)

translations.define("ECommerceOrder.status-refund",
    ca = u"Devolució",
    es = u"Devolución",
    en = u"Refund"
)

translations.define("ECommerceOrder.status-failed",
    ca = u"Cancel·lada",
    es = u"Cancelada",
    en = u"Cancelled"
)

translations.define("ECommerceOrder.purchases",
    ca = u"Contingut de la comanda",
    es = u"Contenido del pedido",
    en = u"Purchases"
)

translations.define("ECommerceOrder.billing",
    ca = u"Facturació",
    es = u"Facturación",
    en = u"Billing"
)

translations.define("ECommerceOrder.total_price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("ECommerceOrder.pricing",
    ca = u"Modificacions al preu",
    es = u"Modificaciones al precio",
    en = u"Pricing"
)

translations.define("ECommerceOrder.total_shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs"
)

translations.define("ECommerceOrder.shipping_costs",
    ca = u"Costos d'enviament aplicats",
    es = u"Costes de envío aplicados",
    en = u"Applied shipping costs"
)

translations.define("ECommerceOrder.total_taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes"
)

translations.define("ECommerceOrder.taxes",
    ca = u"Taxes aplicades",
    es = u"Tasas aplicadas",
    en = u"Applied taxes"
)

translations.define("ECommerceOrder.total",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)

# ECommercePurchase
#------------------------------------------------------------------------------
translations.define("ECommercePurchase",
    ca = u"Línia de comanda",
    es = u"Linea de pedido",
    en = u"Purchase"
)

translations.define("ECommercePurchase-plural",
    ca = u"Línies de comanda",
    es = u"Lineas de pedido",
    en = u"Purchases"
)

translations.define("ECommercePurchase.order",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Order"
)

translations.define("ECommercePurchase.product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define("ECommercePurchase.quantity",
    ca = u"Quantitat",
    es = u"Cantidad",
    en = u"Quantity"
)

translations.define("ECommercePurchase.billing",
    ca = u"Facturació",
    es = u"Facturación",
    en = u"Billing"
)

translations.define("ECommercePurchase.total_price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define("ECommercePurchase.pricing",
    ca = u"Modificacions al preu",
    es = u"Modificaciones al precio",
    en = u"Pricing"
)

translations.define("ECommercePurchase.total_shipping_costs",
    ca = u"Costos d'enviament",
    es = u"Costes de envío",
    en = u"Shipping costs"
)

translations.define("ECommercePurchase.shipping_costs",
    ca = u"Costos d'enviament aplicats",
    es = u"Costes de envío aplicados",
    en = u"Applied shipping costs"
)

translations.define("ECommercePurchase.total_taxes",
    ca = u"Taxes",
    es = u"Tasas",
    en = u"Taxes"
)

translations.define("ECommercePurchase.taxes",
    ca = u"Taxes aplicades",
    es = u"Tasas aplicadas",
    en = u"Applied taxes"
)

translations.define("ECommercePurchase.total",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)

# ECommerceBillingConcept
#------------------------------------------------------------------------------
translations.define("ECommerceBillingConcept",
    ca = u"Concepte de facturació",
    es = u"Concepto de facturación",
    en = u"Billing concept"
)

translations.define("ECommerceBillingConcept-plural",
    ca = u"Conceptes de facturació",
    es = u"Conceptos de facturación",
    en = u"Billing concepts"
)


translations.define("ECommerceBillingConcept.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("ECommerceBillingConcept.enabled",
    ca = u"Activa",
    es = u"Activa",
    en = u"Enabled"
)

translations.define("ECommerceBillingConcept.start_date",
    ca = u"Data d'inici",
    es = u"Fecha de inicio",
    en = u"Start date"
)

translations.define("ECommerceBillingConcept.end_date",
    ca = u"Data de fi",
    es = u"Fecha de fin",
    en = u"End date"
)

translations.define("ECommerceBillingConcept.hidden",
    ca = u"Ocult",
    es = u"Oculto",
    en = u"Hidden"
)

translations.define("ECommerceBillingConcept.scope",
    ca = u"Àmbit",
    es = u"Ámbito",
    en = u"Scope"
)

translations.define("ECommerceBillingConcept.scope-order",
    ca = u"Comanda",
    es = u"Pedido",
    en = u"Order"
)

translations.define("ECommerceBillingConcept.scope-purchase",
    ca = u"Línia de comanda",
    es = u"Linea de pedido",
    en = u"Purchase"
)

translations.define("ECommerceBillingConcept.condition",
    ca = u"Condició",
    es = u"Condición",
    en = u"Condition"
)

translations.define("ECommerceBillingConcept.eligible_regions",
    ca = u"Regions",
    es = u"Regiones",
    en = u"Regions"
)

translations.define("ECommerceBillingConcept.eligible_products",
    ca = u"Productes",
    es = u"Productos",
    en = u"Products"
)

translations.define("ECommerceBillingConcept.eligible_roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

translations.define("ECommerceBillingConcept.implementation",
    ca = u"Valor",
    es = u"Valor",
    en = u"Value"
)

# Initialization
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.catalog_page.title",
    ca = u"Botiga",
    es = u"Tienda",
    en = u"Shop"
)

translations.define("woost.extensions.ecommerce.catalog_controller.title",
    ca = u"Controlador de catàleg de productes",
    es = u"Controlador de catálogo de productos",
    en = u"Product catalog controller"
)

translations.define("woost.extensions.ecommerce.catalog_template.title",
    ca = u"Plantilla de catàleg de productes",
    es = u"Plantilla de catálogo de productos",
    en = u"Product catalog template"
)

translations.define("woost.extensions.ecommerce.basket_page.title",
    ca = u"Cistella de la compra",
    es = u"Cesta de la compra",
    en = u"Shopping basket"
)

translations.define("woost.extensions.ecommerce.basket_controller.title",
    ca = u"Controlador per la cistella de la compra",
    es = u"Controlador para la Cesta de la compra",
    en = u"Shopping basket controller"
)

translations.define("woost.extensions.ecommerce.basket_template.title",
    ca = u"Plantilla per cistella de la compra",
    es = u"Plantilla para cesta de la compra",
    en = u"Shopping basket template"
)

translations.define("woost.extensions.ecommerce.checkout_page.title",
    ca = u"Dades de la comanda",
    es = u"Datos del pedido",
    en = u"Checkout"
)

translations.define("woost.extensions.ecommerce.checkout_controller.title",
    ca = u"Controlador de recollida de dades de comanda de la botiga",
    es = u"Controlador de recojida de datos de pedido de la tienda",
    en = u"Shop checkout controller"
)

translations.define("woost.extensions.ecommerce.checkout_template.title",
    ca = u"Plantilla de recollida de dades de comanda de la botiga",
    es = u"Plantilla de recojida de datos de pedido de la tienda",
    en = u"Shop checkout template"
)

translations.define("woost.extensions.ecommerce.summary_page.title",
    ca = u"Sumari de la comanda",
    es = u"Sumario del pedido",
    en = u"Order summary"
)

translations.define("woost.extensions.ecommerce.summary_controller.title",
    ca = u"Controlador de sumari de comanda de la botiga",
    es = u"Controlador de sumario de pedido de la tienda",
    en = u"Shop order summary controller"
)

translations.define("woost.extensions.ecommerce.summary_template.title",
    ca = u"Plantilla de sumari de comanda de la botiga",
    es = u"Plantilla de sumario de pedido de la tienda",
    en = u"Shop order summary template"
)

translations.define("woost.extensions.ecommerce.success_page.title",
    ca = u"Comanda completada",
    es = u"Pedido completado",
    en = u"Order completed"
)

translations.define("woost.extensions.ecommerce.success_page.body",
    ca = u"La teva comanda s'ha processat correctament.",
    es = u"Tu pedido se ha procesado correctamente.",
    en = u"Your order has been completed successfully."
)

translations.define("woost.extensions.ecommerce.failure_page.title",
    ca = u"Comanda cancel·lada",
    es = u"Pedido cancelado",
    en = u"Order cancelled"
)

translations.define("woost.extensions.ecommerce.failure_page.body",
    ca = u"La teva comanda ha estat cancel·lada.",
    es = u"Tu pedido ha sido cancelado.",
    en = u"Your order has been cancelled."
)

translations.define("woost.extensions.ecommerce.product_controller.title",
    ca = u"Controlador de detall de producte",
    es = u"Controlador de detalle de producto",
    en = u"Shop product detail controller"
)

translations.define("woost.extensions.ecommerce.product_template.title",
    ca = u"Plantilla de detall de producte",
    es = u"Plantilla de detalle de producto",
    en = u"Shop product detail template"
)

# Notices
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.product_added_notice",
    ca = lambda product: 
        u"S'ha afegit <strong>%s</strong> a la cistella"
        % translations(product),
    es = lambda product: 
        u"Se ha añadido <strong>%s</strong> a la cesta"
        % translations(product),
    en = lambda product: 
        u"<strong>%s</strong> added to the shopping basket"
        % translations(product)
)


translations.define(
    "woost.extensions.ecommerce.set_quantities_notice",
    ca = u"S'han actualitzat les quantitats",
    es = u"Se han actualizado las cantidades",
    en = u"Product quantities have been updated"
)

translations.define(
    "woost.extensions.ecommerce.delete_purchase_notice",
    ca = lambda product: 
        u"S'ha tret <strong>%s</strong> de la cistella"
        % translations(product),
    es = lambda product: 
        u"Se ha quitado <strong>%s</strong> de la cesta"
        % translations(product),
    en = lambda product: 
        u"<strong>%s</strong> has been removed from the shopping basket"
        % translations(product)
)

translations.define(
    "woost.extensions.ecommerce.empty_basket_notice",
    ca = u"S'ha buidat la cistella",
    es = u"Se ha vaciado la cesta",
    en = u"The shopping basket has been cleared"
)

# ProductView
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.Product.add_product_form.title",
    ca = u"Afegir a la cistella",
    es = u"Añadir a la cesta",
    en = u"Add to basket"
)

translations.define(
    "woost.extensions.ecommerce.Product.add_product_form.submit_button",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define(
    "woost.extensions.ecommerce.ProductPage.back_link",
    ca = u"Tornar al catàleg",
    es = u"Volver al catálogo",
    en = u"Return to the catalog"
)

translations.define(
    "woost.extensions.ecommerce.ProductPage.checkout_button",
    ca = u"Continuar la compra",
    es = u"Continuar la compra",
    en = u"Checkout"
)

# OrderStep
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.OrderStep.catalog_button",
    ca = u"Veure més productes",
    es = u"Ver más productos",
    en = u"See more products"
)

translations.define(
    "woost.extensions.ecommerce.OrderStep.back_button",
    ca = u"Tornar endarrere",
    es = u"Volver atrás",
    en = u"Go back"
)

translations.define(
    "woost.extensions.ecommerce.OrderStep.proceed_button",
    ca = u"Continuar la compra",
    es = u"Continuar la compra",
    en = u"Proceed"
)

translations.define(
    "woost.extensions.ecommerce.OrderStep.submit_button",
    ca = u"Confirmar la compra",
    es = u"Confirmar la compra",
    en = u"Submit order"
)

# BasketPage
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.BasketPage.back_link",
    ca = u"Tornar al catàleg",
    es = u"Volver al catálogo",
    en = u"Return to the catalog"
)

# BasketView
#------------------------------------------------------------------------------
translations.define(
    "Basket.product",
    ca = u"Producte",
    es = u"Producto",
    en = u"Product"
)

translations.define(
    "Basket.quantity",
    ca = u"Quantitat",
    es = u"Cantidad",
    en = u"Quantity"
)

translations.define(
    "Basket.price",
    ca = u"Preu",
    es = u"Precio",
    en = u"Price"
)

translations.define(
    "Basket.total",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)

translations.define(
    "SetQuantitiesForm-MinValueError",
    ca = u"No es pot demanar menys d'una unitat d'un producte",
    es = u"No se puede solicitar menos de una unidad de un producto",
    en = u"Can't request less than one unit of a product"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.basket_table_total_header",
    ca = u"Total",
    es = u"Total",
    en = u"Total"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.delete_purchase_button",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.empty_basket_button",
    ca = u"Buidar la cistella",
    es = u"Vaciar la cesta",
    en = u"Empty the basket"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.set_quantities_button",
    ca = u"Establir quantitats",
    es = u"Establecer cantidades",
    en = u"Set quantities"
)

translations.define(
    "woost.extensions.ecommerce.BasketView.empty_basket_notice",
    ca = u"La cistella de la compra està buida.",
    es = u"La cesta de la compra está vacía.",
    en = u"The shopping basket is empty."
)

# Discount
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.Discount.end_date",
    ca = lambda end_date:
        u"fins al " + translations(end_date, style = DATE_STYLE_TEXT),
    es = lambda end_date:
        u"hasta el " + translations(end_date, style = DATE_STYLE_TEXT),
    en = lambda end_date:
        u"until " + translations(end_date, style = DATE_STYLE_TEXT)
)

# Basket indicator
#------------------------------------------------------------------------------
translations.define("woost.extensions.ecommerce.BasketIndicator",
    ca = lambda count: 
        plural2(
            count,
            u"<strong>1</strong> producte", 
            u"<strong>%d</strong> productes" % count
        ) + u" a la cistella",
    es = lambda count: 
        plural2(
            count,
            u"<strong>1</strong> producto", 
            u"<strong>%d</strong> productos" % count
        ) + u" en la cesta",
    en = lambda order: 
        plural2(
            count,
            u"<strong>1</strong> product", 
            u"<strong>%d</strong> products" % count
        ) + u" in the shopping basket"
)

# SummaryOrderStep
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.ecommerce.SummaryOrderStep.modify_basket_link",
    ca = u"Modificar el contingut de la comanda",
    es = u"Modificar el contenido del pedido",
    en = u"Edit the shopping basket"
)

translations.define(
    "woost.extensions.ecommerce.SummaryOrderStep.modify_checkout_link",
    ca = u"Modificar les dades de la comanda",
    es = u"Modificar los datos del pedido",
    en = u"Edit checkout data"
)

