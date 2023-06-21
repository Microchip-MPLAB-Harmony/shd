<#--  =====================
      MACRO mhc_process_pios
      ===================== -->
<#compress>
<#macro mhc_process_pios>
    <#assign pioOutList = []>
    <#list 1..core.PIO_PIN_TOTAL as i>
        <#assign funcType = "core.PIN_" + i + "_FUNCTION_TYPE">
        <#assign funcName = "core.PIN_" + i + "_FUNCTION_NAME">
        <#assign pinDir = "core.PIN_" + i + "_DIR">
        <#if funcType?eval?has_content>
            <#if (funcType?eval == "GPIO")>
                <#if pinDir?eval?has_content>
                    <#if (pinDir?eval == "Out")>
                        <#if funcName?eval?has_content>
                            <#assign pioOutList = pioOutList + [funcName?eval]>
                        </#if>
                    </#if>
                </#if>
            </#if>
        </#if>
    </#list>
</#macro>

<#--  =====================
      MACRO execution
      ===================== -->
<@mhc_process_pios/>
</#compress>
<#if (pioOutList?size > 0)>
    <#lt>   /* Switch off LEDs */
    <#list pioOutList as pin>
        <#if pin?lower_case?contains("led")>
            <#lt>   BSP_${pin}_Off();
        </#if>
    </#list>
</#if>
<#--
/*******************************************************************************
 End of File
*/
-->
