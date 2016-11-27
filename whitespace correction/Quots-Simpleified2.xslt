<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<!-- This outermost template asks to match all tags (ie root tag "/")-->
	<!-- side note: <xsl:text>&#x0A;</xsl:text> amounts to the same request as:
	<xsl:text>
</xsl:text>	

<xsl:text>&#x0A;</xsl:text><Writefilepath><xsl:value-of select="/Quots/QuotVerificationInstance/metadata/filepath[@path]" /></Writefilepath>
	 
	Looks neater in my opinon -->
	<xsl:template match="/">	
	 <Quots>
	 <xsl:apply-templates select="/Quots/QuotVerificationInstance/QuotVerified"/>
	 <xsl:text>&#x0A;</xsl:text></Quots>
	 <xsl:text>&#x0A;</xsl:text>
	</xsl:template>

	<!-- This outer template asks to match all QuotVerified tags -->
	<xsl:template match="QuotVerified">
	  <xsl:text>&#x0A;</xsl:text><Quot>
	  <xsl:text>&#x0A;</xsl:text><Quot_id><xsl:value-of select="@id"/></Quot_id>
      <xsl:text>&#x0A;</xsl:text><quotText><xsl:apply-templates select="quotText"/></quotText>
	  <xsl:text>&#x0A;</xsl:text><writefilepath><xsl:value-of select="../metadata/filepath/@path"/></writefilepath>
	  <xsl:text>&#x0A;</xsl:text></Quot>
	</xsl:template>
	
	<!-- This inner template asks to match all text (xml or plain) found in the quotText tag -->
	<xsl:template match="ellip|b|i|catchword">
		<xsl:element name="{name(.)}">
			<xsl:apply-templates/>
		</xsl:element>
	</xsl:template>
	
	<!-- This inner most template asks to match all QuotUnverified/biblio tags and igonre them -->
	<xsl:template match="QuotUnverified|biblioInfo"/>
</xsl:stylesheet>