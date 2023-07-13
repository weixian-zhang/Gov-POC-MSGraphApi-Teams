terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.64.0"
    }
  }
}

provider "azurerm" {
  features {}
}


module "vnet" {
  source = "./vnet"
  
  vnet = var.vnet
  vnet_address_spaces = var.vnet_address_spaces
  resource_group_name = var.resource_group_name
  location = var.location
  subnets = var.subnets
}