
variable "location" {
  default = "southeastasia"
}
  
variable "resource_group_name" {
  default = "rg-dsta-teams-app"
}


variable "vnet" {
    default = "vnet_apps"
}

variable "vnet_address_spaces" {
    type = list(string)
    default = [ "10.0.0.0/16" ]
}

variable "subnets" {
    type = list(object({
        name           = string
        address_prefix = string
        security_group = optional(object({
          name = string
          security_rules = optional(list(object({
            name                       = string
            priority                   = number
            direction                  = string
            access                     = string
            protocol                   = string
            source_port_range          = string
            destination_port_range     = string
            source_address_prefix      = string
            destination_address_prefix = string
          })))
        }))
    }))
}