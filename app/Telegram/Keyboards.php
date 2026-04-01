<?php

namespace App\Telegram;

class Keyboards
{
    public static function mainMenu(int $userId): array
    {
        $rows = [
            [
                ['text' => 'Reminders',      'callback_data' => 'view:reminders'],
                ['text' => 'New Log Entry',  'callback_data' => 'log:start'],
            ],
            [
                ['text' => 'Browse Recipes', 'callback_data' => 'recipe:categories'],
            ],
        ];

        if (Guards::isAdmin($userId)) {
            $rows[] = [['text' => 'Admin Panel', 'callback_data' => 'admin:menu']];
        }

        return ['inline_keyboard' => $rows];
    }

    public static function backButton(string $callbackData = 'main:menu', string $label = '« Back'): array
    {
        return ['inline_keyboard' => [[['text' => $label, 'callback_data' => $callbackData]]]];
    }

    public static function adminMenu(): array
    {
        return [
            'inline_keyboard' => [
                [['text' => 'Manage Reminders',        'callback_data' => 'admin:rem:menu']],
                [['text' => 'Manage Log Categories',    'callback_data' => 'admin:lcat:menu']],
                [['text' => 'Manage Recipe Categories', 'callback_data' => 'admin:rcat:menu']],
                [['text' => 'Add Recipe',               'callback_data' => 'admin:rec:add']],
                [['text' => '« Main Menu',              'callback_data' => 'main:menu']],
            ],
        ];
    }
}
