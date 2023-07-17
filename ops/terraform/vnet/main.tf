locals = {
    emptyNSG = {
        name                       = ""
        priority                   = 500
        direction                  = "Inbound"
        access                     = "Deny"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "443"
        source_address_prefix      = "10.0.0.0/24"
        destination_address_prefix = "10.0.1.0/24"
    }
}

resource "azurerm_network_security_group" "nsg" {
  for_each = { for v in var.subnets : v.name => v.security_group}
  name                = each.value.name
  resource_group_name = var.resource_group_name
  location            = var.location

  dynamic "security_rule" {
    for_each = { 
        for subnet in var.subnets : 
        subnet.name => [ for rule in security_group.security_rules: rule ]
    }

    content {
      name                        = security_rule.value["name"]
      priority                    = security_rule.value["priority"]
      direction                   = security_rule.value["direction"]
      access                      = security_rule.value["access"]
      protocol                    = security_rule.value["protocol"]
      source_port_range           = security_rule.value["source_port_range"]
      destination_port_range      = security_rule.value["destination_port_range"]
      source_address_prefix       = security_rule.value["source_address_prefix"]
      destination_address_prefix  = security_rule.value["destination_address_prefix"]
    }
  }
}

resource "azurerm_virtual_network" "example" {
  name                = var.vnet
  resource_group_name = var.resource_group_name
  location            = var.location
  address_space       = var.vnet_address_spaces
}